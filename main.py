import os
import platform
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

print(f"DEBUG: roFs={os.getenv("roFs")}")
if not os.getenv("roFs") == "false":
    import youtube_nocache as yt
else:
    import logging
    import youtube as yt
    logger = logging.getLogger(__name__)
    if not os.path.exists("./logs/"):
        os.mkdir(path="./logs/")
    logging.basicConfig(filename='./logs/youtube.log', level=logging.DEBUG)

isWin32 = platform.system() == "Windows"
if isWin32:
    yt.init(paths={
        "deno": "./bin/deno.exe",
        "ffmpeg": "./bin/ffmpeg.exe",
        "yt-dlp": "./bin/yt-dlp.exe",
    })
else:
    yt.init(paths={
        "deno": "./bin/deno",
        "ffmpeg": "./bin/ffmpeg",
        "yt-dlp": "./bin/yt-dlp",
    })


app = FastAPI(
    title="YouTube API",
    description="An alternative for the Official YT Api",
    version="1.10.15",
    root_path="",
    redoc_url="/newdocs"
)

# noinspection PyTypeChecker
app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"]
)


@app.get(path="/")
def page_root():
    return {"detail": {"description": app.description, "version": app.version}, "success": True}


@app.get(path="/help")
def page_help():
    return {
        "detail": {
            "root": app.root_path,
            "docs": app.docs_url,
            "redocs": app.redoc_url,
            "help": "/help",
            "get video infos": "/video/{vid}/info?raw=[BOOL]",
            "get video download links": "/video/{vid}/urls",
            "get video subtitles": "/video/{vid}/sub?lang=[lang]&auto=[BOOL]",
            "get video available subtitles": "/video/{vid}/subs?auto=[BOLL]",
        },
        "success": True
    }


@app.get(path="/video/{vid}/info")
def page_video_info(vid: str, raw: bool = False):
    video = yt.Video()
    if not video.is_valid_id(vid):
        print(f"ERROR: the id '{vid}' is not in the valid format")
        return {"detail": "Error: this id is not in the valid format", "success": False}
    print(f"DEBUG: Requesting data for vid:{vid}; raw:{raw}")
    data = video.infos(vid, raw)
    print(f"DEBUG: data:{data}")
    return {"detail": data, "success": not str(data).startswith("ERROR")}


@app.get(path="/video/{vid}/urls")
def page_video_urls(vid: str):
    video = yt.Video()
    if not video.is_valid_id(vid):
        print(f"DEBUG: the id '{vid}' is not in the valid format")
        return {"detail": "Error: this id is not in the valid format", "success": False}
    print(f"DEBUG: Requesting urls for vid:{vid}")
    urls = video.urls(vid)
    print(f"DEBUG: urls:{urls}")
    return {"detail": urls, "success": not str(urls).startswith("ERROR")}


@app.get(path="/video/{vid}/sub")
def page_video_subtitles(vid: str, lang: str, auto: bool = False):
    video = yt.Video()
    if not video.is_valid_id(vid):
        print(f"DEBUG: the id '{vid}' is not in the valid format")
        return {"detail": "Error: this id is not in the valid format", "success": False}
    print(f"DEBUG: Requesting subtitles for vid:{vid}")
    subtitles = video.subtitles(vid, lang, auto)
    print(f"DEBUG: subtitles:{subtitles}")
    return {"detail": subtitles, "success": not str(subtitles).startswith("ERROR")}


@app.get(path="/video/{vid}/subs")
def page_video_subtitles(vid: str, auto: bool = False):
    video = yt.Video()
    if not video.is_valid_id(vid):
        print(f"DEBUG: the id '{vid}' is not in the valid format")
        return {"detail": "Error: this id is not in the valid format", "success": False}
    print(f"DEBUG: Requesting available subtitles for vid:'{vid}' and mode:{'auto' if auto else 'custom'}")
    available_subtitles = video.available_subtitles(vid, auto)
    print(f"DEBUG: available subtitles:{available_subtitles}")
    return {"detail": available_subtitles, "success": not str(available_subtitles).startswith("ERROR")}

if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=2684,
        ssl_keyfile="./certs/key.pem",
        ssl_certfile="./certs/cert.pem",
        use_colors=True
    )
