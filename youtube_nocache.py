import re
import requests
import yt_dlp

paths = {}
ytdlp_opts = {}


def init(**kwargs):
    if kwargs.get('paths', None) is None:
        raise KeyError
    global paths, ytdlp_opts
    paths = kwargs.get('paths')
    ytdlp_opts = {
        'simulate': True,
        'forceurl': True,
        'noplaylist': True,
        'js_runtimes': {
            'deno': {
                'path': paths['deno']
            }
        },
        "ffmpeg_location": paths['ffmpeg'],
        'extractor-args': 'youtube:player_client=web_safari'
    }


class Video(object):
    def __init__(self):
        pass

    @staticmethod
    def _extract(__info: list):
        return {
            "url": f"https://le-herisson.github.io/embed/youtube?id={__info[0].get('id', KeyError)}",
            "stats": {
                "likes": __info[0].get('like_count', 0),
                "dislikes": __info[1].get('dislikes', 0),
                "view_count": __info[0].get('view_count', 0),
                "comment_count": __info[0].get('comment_count', 0)
            },
            "channel": {
                "name": __info[0].get('uploader', KeyError),
                "handle": __info[0].get('uploader_id', KeyError),
                "is_verified": __info[0].get('channel_is_verified', False)
            },
            "res": {
                "height": __info[0].get('height', KeyError),
                "width": __info[0].get('width', KeyError)
            },
            "thumbnail": {
                "height": __info[2].get('thumbnail_height', None),
                "width": __info[2].get('thumbnail_width', None),
                "url": f"https://i.ytimg.com/vi/{__info[0].get('id', KeyError)}/hqdefault.jpg"
            },
            "live": {
                "status": __info[0].get('live_status', None),
                "is": __info[0].get('is_live', False),
                "was": __info[0].get('was_live', False)
            },
            "general": {
                "title": __info[0].get('title', None),
                "tags": __info[0].get('tags') or [],
                "type": __info[0].get('media_type', None),
                "timestamp": __info[0].get('timestamp', None),
                "duration": __info[0].get('duration', None),
                "duration_string": __info[0].get('duration_string', None),
                "genre": __info[0].get('categories', None),
                "description": __info[0].get('description', None),
                "playable_in_embed": __info[0].get('playable_in_embed', False)
            },
            "deleted": __info[1].get('deleted', None),
            "fps": __info[0].get('fps', None),
            "chapters": __info[0].get('chapters') or []
        }

    @staticmethod
    def _extract_objects(__info):
        video_obj, audio_obj = (None, None)
        for obj in __info['formats']:
            if not obj['video_ext'] == "none":
                video_obj = obj
            if not obj['audio_ext'] == "none":
                audio_obj = obj
        if video_obj is None or audio_obj is None:
            raise RuntimeError
        return [video_obj, audio_obj]

    @staticmethod
    def _available_subtitles(__subs: list):
        subs = []
        for obj in __subs:
            subs = subs + [obj]
        return subs

    @staticmethod
    def is_valid_id(_vid: str):
        return True if re.search(pattern=r"([a-zA-Z0-9_-]{11})", string=_vid) else False

    @staticmethod
    def infos(_vid: str, _raw: bool = False):
        try:
            res1 = requests.get(f"https://returnyoutubedislikeapi.com/votes?videoId={_vid}")
            res2 = requests.get(f"https://youtube.com/oembed?url=https://youtu.be/{_vid}")
            if not res1.status_code == 200 or not res2.status_code == 200:
                print(f"ERROR: {'res1': {res1.status_code}, 'res2': {res2.status_code}}")
                raise ConnectionError
            with yt_dlp.YoutubeDL(ytdlp_opts) as ydl:
                infos = [ydl.extract_info(f"https://youtu.be/{_vid}", download=False), res1.json(), res2.json()]
            return infos if _raw else Video._extract(infos)
        except Exception as e:
            print(f"Exception: {e}")
            return f"ERROR: {e}"

    @staticmethod
    def urls(_vid: str):
        try:
            with yt_dlp.YoutubeDL(ytdlp_opts) as ydl:
                infos = ydl.extract_info(f"https://youtu.be/{_vid}", download=False)
                urls = Video._extract_objects(infos)
                print(f"DEBUG: _extract_objects(infos)={urls}")
                return {
                    "video": urls[0]['url'],
                    "audio": urls[1]['url'],
                    "video_frmt": urls[0]['format'],
                    "audio_frmt": urls[1]['format']
                }
        except Exception as e:
            print(f"Exception: {e}")
            return f"ERROR: Video and/or audio is unavailable for video '{_vid}'; exception msg: {e}"

    @staticmethod
    def subtitles(_vid: str, _lang: str, _auto: bool = False):
        try:
            with yt_dlp.YoutubeDL(ytdlp_opts) as ydl:
                subtitles = ydl.extract_info(f"https://youtu.be/{_vid}", download=False)[
                    'automatic_captions' if _auto else 'subtitles']
            if _lang not in Video._available_subtitles(subtitles):
                raise LookupError
            return subtitles[_lang]
        except Exception as e:
            print(f"Exception: {e}")
            return f"ERROR: Subtitles is unavailable for video='{_vid}'; mode='{'auto' if _auto else 'custom'}'; lang='{_lang}'; exception msg: {e}"

    @staticmethod
    def available_subtitles(_vid: str, _auto: bool = False):
        try:
            with yt_dlp.YoutubeDL(ytdlp_opts) as ydl:
                subtitles = ydl.extract_info(f"https://youtu.be/{_vid}", download=False)[
                    'automatic_captions' if _auto else 'subtitles']
            return Video._available_subtitles(subtitles)
        except Exception as e:
            print(f"Exception: {e}")
            return f"ERROR: Subtitles is unavailable for video='{_vid}'; mode='{'auto' if _auto else 'custom'}'; exception msg: {e}"
