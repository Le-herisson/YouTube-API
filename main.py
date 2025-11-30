import re
import requests
import yt_dlp

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="YouTube API",
    description="An alternative for the Official YT Api",
    version="0.5",
    root_path="",
    redoc_url="/newdocs"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"]
)


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
            "get video info": "/video/{vid}/info",
            "get video subtitles": "/video/{vid}/sub",
            "get video download link": "/video/{vid}/download"
        },
        "success": True
    }


@app.get(path="/video/{vid}/info")
def page_video_info(vid: str):
    if not re.search(pattern=r"([a-zA-Z0-9_-]{11})", string=vid):
        return {"detail": "Error: this id is not in a valid format", "success": False}

    try:
        res1 = requests.get(f"https://returnyoutubedislikeapi.com/votes?videoId={vid}")
        res2 = requests.get(f"https://youtube.com/oembed?url=https://youtu.be/{vid}")
    except Exception as e:
        print(f"ERROR:    {e}")
        return {"detail": f"Error: {e}", "success": False}

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
            with yt_dlp.YoutubeDL({'quiet': True, 'simulate': True, 'format': 'best', 'noplaylist': True}) as ydl:
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


@app.get(path="/video/{vid}/download")
def page_video_download(vid: str, vformat: str):
    if not re.search(pattern=r"[a-zA-Z0-9_-]{11}", string=vid):
        return {"detail": "Error: this id is not in a valid format", "success": False}

    if vformat == "mp4":
        with yt_dlp.YoutubeDL({'quiet': True, 'simulate': True, 'forceurl': True, 'format': 'best'}) as ydl:
            return {"detail": ydl.extract_info(f"https://youtu.be/{vid}", download=False)['url'], "success": True}
    elif vformat == "mp3":
        with yt_dlp.YoutubeDL({
            'quiet': True, 'simulate': True, 'forceurl': True, 'extract_audio': True, 'format': 'bestaudio',
            'audio-format': 'opus'
        }) as ydl:
            return {"detail": ydl.extract_info(f"https://youtu.be/{vid}", download=False)['url'], "success": True}
    elif vformat == "mkv":
        return {"detail": f"Error: this format is not supported yet. '{vformat}'", "success": False}
    else:
        return {"detail": f"Error: this format is not valid. '{vformat}'", "success": False}


@app.get(path="/video/{vid}/sub")
def page_video_subtitles(vid: str):
    if not re.search(pattern=r"([a-zA-Z0-9_-]{11})", string=vid):
        return {"detail": "Error: this id is not in a valid format", "success": False}
    else:
        with yt_dlp.YoutubeDL({'quiet': True, 'simulate': True, 'noplaylist': True}) as ydl:
            return {
                "detail": ydl.extract_info(f"https://youtu.be/{vid}", download=False)['subtitles'],
                "success": True
            }
