import re

from streamlink.plugin import Plugin, pluginmatcher
from streamlink.plugin.api import validate
from streamlink.stream import HLSStream

_post_schema = validate.Schema({
        'hentai_video': validate.Schema({
            'name': str,
            'is_visible': bool
            }),
        'videos_manifest': validate.Schema({
            'servers': validate.Schema([{
                'streams': validate.Schema([{
                    'height': str,
                    'url': str,
                    'id': int
                }])
            }])
        }),
})

@pluginmatcher(re.compile(
    r"https?://hanime\.tv/videos/hentai/(?P<videoid>[a-zA-Z0-9_-]+)"
))

class hanimetv(Plugin):

    def get_title(self):
        return self.title

    def get_author(self):
        return "hanime"

    def get_category(self):
        return "VOD"

    def _get_streams(self):
        videoid = self.match.group("videoid")

        api_call = "https://hanime.tv/api/v8/video?id={0}".format(videoid)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0",
            "Referer": self.url,
        }

        res = self.session.http.get(api_call, headers=headers)
        data = self.session.http.json(res, schema=_post_schema)

        if not data:
            self.logger.info("Not a valid url.")
            return

        self.title = data["hentai_video"]["name"]

        self.logger.info("Video Name: {0}".format(self.title))

        for stream in data["videos_manifest"]["servers"][0]["streams"]:
            if (stream["url"]):
                q = "{0}p".format(stream["height"])
                s = HLSStream(self.session, stream["url"])
                yield q, s
            else:
                q = "{0}p".format(stream["height"])
                u = "https://hanime.tv/api/v8/m3u8s/{0}.m3u8".format(stream["id"])
                s = HLSStream(self.session, u)
                yield q, s

__plugin__ = hanimetv
