import json
import re
import requests
import yt_dlp

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

formats = {"best": "bestvideo+bestaudio/best", "4K": "res:3840,fps", "2K": "res:2048,fps", "1080p": "res:1080,fps",
           "720p": "res:720,fps", "480p": "res:480,fps", "lower": "wv*+wa/w"}


def valid_vid(vid: str):
    return re.search(pattern=r"([a-zA-Z0-9_-]{11})", string=vid)


def valid_quality(q: str):
    return q in formats


app = FastAPI(title="YouTube API", description="An alternative for the Official YT Api", version="0.9", root_path="",
              redoc_url="/newdocs")

app.add_middleware(middleware_class=CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["GET"],
                   allow_headers=["*"])


@app.get(path="/")
def page_root():
    return {"detail": f"{app.description}", "success": True}


@app.get(path="/help")
def page_help():
    return {
        "detail": {
            "root": "/",
            "docs": "/docs",
            "help": "/help",
            "get video info": "/video/{vid}/info?raw=[BOOL]",
            "get video subtitles": "/video/{vid}/sub",
            "get video download link":
                "/video/{vid}/url?vf=(mp3 | mp4)&q=(best | 4K | 2K | 1080p | 720p | 480p | lower)",
            "get channel info": "/channel/{handle}/info?raw=[BOOL]"
        },
        "success": True
    }


@app.get(path="/video/{vid}/info")
def page_video_info(vid: str, raw: bool = False):
    if not valid_vid(vid):
        return {"detail": "Error: this id is not in a valid format", "success": False}
    try:
        if raw:
            print("[infos] Trying")
            with yt_dlp.YoutubeDL({'quiet': True, 'simulate': True, 'noplaylist': True}) as ydl:
                print("[infos] Success")
                return {"detail": ydl.extract_info(f"https://youtu.be/{vid}", download=False), "success": True}
        else:
            res1 = requests.get(f"https://returnyoutubedislikeapi.com/votes?videoId={vid}")
            res2 = requests.get(f"https://youtube.com/oembed?url=https://youtu.be/{vid}")

            if not res1.status_code == 200 or not res2.status_code == 200:
                return {
                    "detail": {
                        "status 1": {res1.status_code},
                        "status 2": {res2.status_code}
                    },
                    "success": False
                }
            else:
                try:
                    with yt_dlp.YoutubeDL({'quiet': True, 'simulate': True, 'noplaylist': True}) as ydl:
                        print("[infos] Trying")
                        info = ydl.extract_info(f"https://youtu.be/{vid}", download=False)
                        print("[infos] Success")
                        hd = False
                        try:
                            info['duration']
                            hd = True
                        except Exception as e:
                            print(f"ERROR:    {e}")
                            pass

                    res1 = res1.json()
                    res2 = res2.json()
                    return {
                        "detail": {
                            "url": f"https://le-herisson.github.io/embed/youtube?id={vid}",
                            "date": res1['dateCreated'],
                            "likes": res1['likes'],
                            "dislikes": res1['dislikes'],
                            "viewCount": res1['viewCount'],
                            "deleted": res1['deleted'],

                            "title": res2['title'],
                            "author": {
                                "name": res2['author_name'],
                                "handle": str(res2['author_url']).replace("https://www.youtube.com/", "")
                            },
                            "type": res2['type'],
                            "res": {
                                "height": res2['height'],
                                "width": res2['width']
                            },
                            "thumbnail": {
                                "height": res2['thumbnail_height'],
                                "width": res2['thumbnail_width'],
                                "url": res2['thumbnail_url']
                            },
                            "length": info['duration'] if hd else "undefined",
                            "tags": info['tags'],
                            "genre": info.get('categories', ['Unknown']),
                            "description": info['description']
                        },
                        "success": True
                    }
                except Exception as e:
                    print("[infos] Failed")
                    print(f"ERROR:    {e}")
                    return {"detail": f"Error: {e}", "success": False}
    except Exception as e:
        print(f"ERROR:    {e}")
        return {"detail": f"Error: {e}", "success": False}


@app.get(path="/video/{vid}/url")
def page_video_url(vid: str, vf: str, q: str = 'best'):
    if not valid_vid(vid):
        return {"detail": "Error: this id is not in a valid format", "success": False}

    if vf not in {'mp3', 'mp4'}:
        return {"detail": f"Error: this format is not valid. '{vf}'", "success": False}
    ytdl_opts = {'quiet': True, 'simulate': True, 'forceurl': True}
    if vf == "mp4":
        if not valid_quality(q):
            return {"detail": "Error: this quality is not in a valid format", "success": False}
        ytdl_opts = {**ytdl_opts, **{'f' if q == "best" or q == "lower" else 'S': formats.get(q)}}
    elif vf == "mp3":
        ytdl_opts = {**ytdl_opts, **{'extract_audio': True, 'format': 'ba[acodec^=mp3]/ba/b', 'audio-format': vf}}
    with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
        print(f"ytdl_opts: {ytdl_opts}")
        if q == "lower":
            return {"detail": 'F*ck, that killed my time too much.', "success": False}
        else:
            return {"detail": ydl.extract_info(f"https://youtu.be/{vid}", download=False)['url'], "success": True}


@app.get(path="/video/{vid}/sub")
def page_video_subtitles(vid: str):
    if not valid_vid(vid):
        return {"detail": "Error: this id is not in a valid format", "success": False}
    else:
        with yt_dlp.YoutubeDL({'quiet': True, 'simulate': True, 'noplaylist': True}) as ydl:
            return {
                "detail": ydl.extract_info(f"https://youtu.be/{vid}", download=False)['subtitles'],
                "success": True
            }


@app.get(path="/channel/{handle}/info")
def page_channel_info(handle: str, raw: bool = False):
    handle = handle.replace('@', '')
    try:
        with yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': True, 'force_generic_extractor': True}) as ydl:
            info = ydl.extract_info(f"https://youtube.com/@{handle}", download=False)
            if raw:
                return info
            else:
                for o in info['thumbnails']:
                    if o['id'] == "banner_uncropped":
                        banner = o['url']
                    elif o['id'] == "avatar_uncropped":
                        pfp = o['url']
                    else:
                        pass
                    print(f"{o['id']}: {o['url']}")
                return {
                    "detail": {
                        "uid": info['channel_id'],
                        "follower_count": info['channel_follower_count'],
                        "description": info['description'],
                        "tags": info['tags'],
                        "banner": banner,
                        "video_count": "soon",
                        "location": "soon",
                        "pfp": pfp,
                        "name": info['channel']
                    },
                    "success": True
                }
    except Exception as e:
        print(f"ERROR:    {e}")
        return {"detail": f"Error: {e}", "success": False}
