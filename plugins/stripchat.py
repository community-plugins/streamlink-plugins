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
            'streamName' : str,
            'topic' : str,
            'viewServers': validate.Schema({'flashphoner-hls': str})
        }),
        "user": validate.Schema({
            'user' : validate.Schema({
                'status' : str,
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

        server = "https://b-{0}.doppiocdn.com/hls/{1}/master/{1}_auto.m3u8?playlistType=standard".format(data["cam"]["viewServers"]["flashphoner-hls"],data["cam"]["streamName"])
        server_src = "https://b-{0}.doppiocdn.com/hls/{1}/master/{1}.m3u8?playlistType=standard".format(data["cam"]["viewServers"]["flashphoner-hls"],data["cam"]["streamName"])
        server0 = "https://edge-hls.doppiocdn.com/hls/{0}/master/{0}_auto.m3u8?playlistType=standard".format(data["cam"]["streamName"])
        server1 = "https://edge-hls.doppiocdn.org/hls/{0}/master/{0}_auto.m3u8?playlistType=standard".format(data["cam"]["streamName"])
        server2 = "https://b-{0}.doppiocdn.org/hls/{1}/{1}.m3u8".format(data["cam"]["viewServers"]["flashphoner-hls"],data["cam"]["streamName"])

        self.logger.info("Stream status: {0}".format(data["user"]["user"]["status"]))

        if (data["user"]["user"]["isLive"] is True and data["user"]["user"]["status"] == "public" and server):
            try:
                self.logger.info("trying server {0}".format(server))
                for s in HLSStream.parse_variant_playlist(self.session,server,headers={'Referer': self.url}).items():
                    yield s
                for s in HLSStream.parse_variant_playlist(self.session,server_src,headers={'Referer': self.url}).items():
                    yield s
            except IOError as err:
                try:
                    self.logger.info("trying fallback server {0}".format(server0))
                    for s in HLSStream.parse_variant_playlist(self.session,server0,headers={'Referer': self.url}).items():
                        yield s
                except IOError as err:
                    try:
                        self.logger.info("trying another fallback server {0}".format(server1))
                        for s in HLSStream.parse_variant_playlist(self.session,server1,headers={'Referer': self.url}).items():
                            yield s
                    except IOError as err:
                        self.logger.info("fallback to default stream : {0}".format(server2))
                        stream = HLSStream(self.session, server2)
                        yield "auto", stream

__plugin__ = Stripchat
