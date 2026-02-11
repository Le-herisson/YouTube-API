import re
import requests
import yt_dlp

paths = {}


def init(**kwargs):
    global paths
    paths = kwargs.get('paths', KeyError)


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
            with yt_dlp.YoutubeDL({
                'quiet': True, 'simulate': True, 'noplaylist': True,
                'js_runtimes': {'deno': {'path': paths['deno']}}, "ffmpeg_location": paths['ffmpeg']
            }) as ydl:
                infos = [ydl.extract_info(f"https://youtu.be/{_vid}", download=False), res1.json(), res2.json()]
            return infos if _raw else Video._extract(infos)
        except Exception as e:
            print(f"Exception: {e}")
            return f"ERROR: {e}"

    @staticmethod
    def urls(_vid: str):
        ytdl_opts = {'simulate': True, 'forceurl': True, 'noplaylist': True,
                     'js_runtimes': {'deno': {'path': paths['deno']}}, "ffmpeg_location": paths['ffmpeg']}
        try:
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                infos = ydl.extract_info(f"https://youtu.be/{_vid}", download=False)
                is_premium = infos['requested_formats'][0]['format_note'] == "Premium"
                if is_premium:
                    print("WARNING: This format is Premium")
                return {
                    "video": infos['formats'][-2]['url'] if is_premium else infos['requested_formats'][0]['url'],
                    "audio": infos['requested_formats'][1]['url'],
                    "video_frmt": infos['formats'][-2]['format'] if is_premium else infos['requested_formats'][0]['format'],
                    "audio_frmt": infos['requested_formats'][1]['format'],
                    "is_premium": is_premium
                }
        except Exception as e:
            print(f"Exception: {e}")
            return f"ERROR: Video and/or audio is unavailable for video '{_vid}'; ytdl_opts: {ytdl_opts}; exception msg: {e}"
