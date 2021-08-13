import re

from streamlink.plugin import Plugin
from streamlink.plugin.api import validate
from streamlink.stream import HLSStream

_url_re = re.compile(r"https?://(\w+\.)?stripchat\.com/(?P<username>[a-zA-Z0-9_-]+)")

_post_schema = validate.Schema(
    {
        "cam": validate.Schema({
                    'streamName' : validate.text,
                    'topic' : validate.text,
                    'viewServers': validate.Schema({'flashphoner-hls': validate.text})
        }),
        "user": validate.Schema({
                    'user' : validate.Schema({
                                'status' : validate.text,
                                'isLive' : bool
                    })
        })
    }
)


class Stripchat(Plugin):
    @classmethod
    def can_handle_url(cls, url):
        return _url_re.match(url)

    def get_title(self):
        return self.title

    def get_author(self):
        return self.author

    def get_category(self):
        return "Live"

    def _get_streams(self):
        match = _url_re.match(self.url)
        username = match.group("username")
        api_call = "https://stripchat.com/api/front/v2/models/username/{0}/cam".format(username)
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": self.url,
        }

        res = self.session.http.get(api_call, headers=headers)
        data = self.session.http.json(res, schema=_post_schema)

        if not data:
            self.logger.info("Not a valid url.")
            return

        self.author = username
        self.title = data["cam"]["topic"]

        server = "https://b-{0}.strpst.com/hls/{1}/master_{1}.m3u8".format(data["cam"]["viewServers"]["flashphoner-hls"],data["cam"]["streamName"])

        server0 = "https://b-{0}.strpst.com/hls/{1}/{1}.m3u8".format(data["cam"]["viewServers"]["flashphoner-hls"],data["cam"]["streamName"])

        self.logger.info("Stream status: {0}".format(data["user"]["user"]["status"]))

        if (data["user"]["user"]["isLive"] is True and data["user"]["user"]["status"] == "public" and server):
            try:
                for s in HLSStream.parse_variant_playlist(self.session,server,headers={'Referer': self.url}).items():
                    yield s
            except IOError as err:
                stream = HLSStream(self.session, server0)
                yield "default", stream

__plugin__ = Stripchat
