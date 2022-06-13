import re

from streamlink.plugin import Plugin, pluginmatcher
from streamlink.plugin.api import validate
from streamlink.stream.hls import HLSStream

@pluginmatcher(re.compile(
    r"https?://(\w+\.)?stripchat\.com/(?P<username>[a-zA-Z0-9_-]+)"
))

class Stripchat(Plugin):

    _data_schema = validate.Schema({
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
    })

    def get_title(self):
        return self.title

    def get_author(self):
        return self.author

    def get_category(self):
        return "NSFW LIVE"

    def _get_streams(self):
        username = self.match.group("username")

        api_url = "https://stripchat.com/api/front/v2/models/username/{0}/cam".format(username)
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": self.url,
        }

        res = self.session.http.get(api_url, headers=headers)
        data = self.session.http.json(res, schema=self._data_schema)

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
