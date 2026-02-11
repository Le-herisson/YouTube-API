import logging
import os
import platform

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import youtube

logger = logging.getLogger(__name__)
if not os.path.exists("./logs/"):
    os.mkdir(path="./logs/")
logging.basicConfig(filename='./logs/youtube.log', level=logging.DEBUG)

isWin32 = platform.system() == "Windows"
if isWin32:
    youtube.init(paths={
        "deno": "./bin/deno.exe",
        "ffmpeg": "./bin/ffmpeg.exe",
        "yt-dlp": "./bin/yt-dlp.exe",
    })
else:
    youtube.init(paths={
        "deno": "./bin/deno",
        "ffmpeg": "./bin/ffmpeg",
        "yt-dlp": "./bin/yt-dlp",
    })

app = FastAPI(
    title="YouTube API",
    description="An alternative for the Official YT Api",
    version="1.10.7",
    root_path="",
    redoc_url="/newdocs"
)

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
            "root": "/",
            "docs": "/docs",
            "redocs": app.redoc_url,
            "help": "/help",
            "get video infos": "/video/{vid}/info?raw=[BOOL]",
            "get video download links": "/video/{vid}/urls",
        },
        "success": True
    }


@app.get(path="/video/{vid}/info")
def page_video_info(vid: str, raw: bool = False):
    video = youtube.Video()
    if not video.is_valid_id(vid):
        logger.error(msg=f"the id '{vid}' is not in the valid format")
        return {"detail": "Error: this id is not in the valid format", "success": False}
    logger.debug(msg=f"Requesting data for vid:{vid}; raw:{raw}")
    data = video.infos(vid, raw)
    logger.debug(msg=f"data:{data}")
    return {"detail": data, "success": not str(data).startswith("ERROR")}


@app.get(path="/video/{vid}/urls")
def page_video_urls(vid: str):
    video = youtube.Video()
    if not video.is_valid_id(vid):
        logger.error(msg=f"the id '{vid}' is not in the valid format")
        return {"detail": "Error: this id is not in the valid format", "success": False}
    logger.debug(msg=f"Requesting urls for vid:{vid}")
    urls = video.urls(_vid=vid)
    logger.debug(msg=f"urls:{urls}")
    return {"detail": urls, "success": not str(urls).startswith("ERROR")}



if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=2684,
        ssl_keyfile="./certs/key.pem",
        ssl_certfile="./certs/cert.pem",
        use_colors=True
    )
