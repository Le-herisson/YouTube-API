import os
import platform
import random
import re
import requests
import yt_dlp

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

Maybe = random.choice(seq=[True, False])
deno_path = "./bin/deno.exe" if platform.system() == "Windows" else "./bin/deno"
formats = {"best": "bestvideo+bestaudio/best", "4K": "res:3840,fps", "2K": "res:2048,fps", "1080p": "res:1080,fps",
           "720p": "res:720,fps", "480p": "res:480,fps", "lower": "wv*+wa/w"}


def valid_vid(vid: str):
    return re.search(pattern=r"([a-zA-Z0-9_-]{11})", string=vid)


def valid_quality(q: str):
    return q in formats


app = FastAPI(title="YouTube API", description="An alternative for the Official YT Api", version="1.9.1", root_path="",
              redoc_url="/newdocs")

app.add_middleware(middleware_class=CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["GET"],
                   allow_headers=["*"])


@app.get(path="/")
def page_root():
    return {"detail": {"description": app.description, "version": app.version}, "success": True}


@app.get(path="/help")
def page_help():
    return {
        "detail": {
            "root": "/",
            "docs": "/docs",
            "help": "/help",
            "get video info": "/video/{vid}/info?raw=[BOOL]",
            "get video subtitles": "/video/{vid}/sub",
            "get video download link": "/video/{vid}/url?vf=(mp3 | mp4)&q=(best | 4K | 2K | 1080p | 720p | 480p | lower)",
            "get channel info": "/channel/{handle}/info?raw=[BOOL]"
        },
        "success": True
    }


# noinspection PyStatementEffect
@app.get(path="/video/{vid}/info")
def page_video_info(vid: str, raw: bool = False):
    if not valid_vid(vid):
        return {"detail": "Error: this id is not in a valid format", "success": False}
    try:
        if raw:
            print("[infos] Trying")
            with yt_dlp.YoutubeDL({'quiet': True, 'simulate': True, 'noplaylist': True,
                                   'js_runtimes': {'deno': {'path': deno_path}}}) as ydl:
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


@app.get(path="/video/{vid}/urls")
def page_video_url(vid: str, q: str = 'best'):
    if not valid_vid(vid):
        return {"detail": "Error: this id is not in a valid format", "success": False}
    ytdl_opts = {'simulate': True, 'forceurl': True, 'noplaylist': True, 'f': formats.get(q),
                 'js_runtimes': {'deno': {'path': deno_path}}}
    # ytdl_opts = {**ytdl_opts, **{'extract_audio': True, 'format': 'ba[acodec^=mp3]/ba/b', 'audio-format': vf}}
    try:
        with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
            print(f"ytdl_opts: {ytdl_opts}")
            if q == "lower":
                return {"detail": 'F*ck, that killed my time too much.', "success": False}
            infos = ydl.extract_info(f"https://youtu.be/{vid}", download=False)
            print(f"INFO:    infos['requested_formats']={infos['requested_formats']}")
            is_premium = infos['requested_formats'][0]['format_note'] == "Premium"
            if is_premium:
                print(f"WARN:     This format is Premium")
            return {
                "detail": {
                    "video": infos['formats'][-2]['url'] if is_premium else infos['requested_formats'][0]['url'],
                    "audio": infos['requested_formats'][1]['url'],
                    "video_frmt": infos['formats'][-2]['format'] if is_premium else infos['requested_formats'][0]['format'],
                    "audio_frmt": infos['requested_formats'][1]['format'],
                    "is_premium": is_premium
                },
                "success": True
            }
    except Exception as e:
        print(f"ERROR:    {e}")
        return {"detail": f"Error: {e}", "success": False}


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


@app.get(path="/channel/{handle}/videos")
def page_channel_videos(handle: str, l: int = 10):
    handle = handle.replace('@', '')
    path = f"videos/{handle}.txt"
    if os.path.exists(path):
        os.remove(path)
    os.system(
        f"yt-dlp --flat-playlist --print-to-file webpage_url \"{path}\" \"https://youtube.com/@{handle}\""
    )
    if platform.system() == "Windows":
        print(f"INFO:     errorlevel={os.system("ECHO %ERRORLEVEL%")}")
    try:
        with open(file=f"{path}", mode="r", encoding="utf-8") as f:
            vids = f.read()
    except Exception as e:
        print(f"ERROR:    {e}")
        return {"detail": f"Error: {e}", "success": False}
    return {
        "detail": {
            "channel": handle,
            "videos": vids
        },
        "success": True
    }
