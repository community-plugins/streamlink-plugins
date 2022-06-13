import random
import re

from streamlink.plugin import Plugin, pluginmatcher
from streamlink.plugin.api import validate
from streamlink.stream import HLSStream

@pluginmatcher(re.compile(
    r"https?://(\w+\.)?camsoda\.com/(?P<username>[a-zA-Z0-9_-]+)/?$"
))

class Camsoda(Plugin):

    _data_schema = validate.Schema(
        {
            "status": validate.any(int, validate.text),
            "token": validate.text,
            "edge_servers": [validate.text],
            "stream_name": validate.text,
        }
    )

    def get_title(self):
        return self.title

    def get_author(self):
        return self.author

    def get_category(self):
        return "NSFW LIVE"

    def _get_streams(self):
        username = self.match.group("username")

        randomid = str(random.randint(1000, 99999))

        api_url = "https://www.camsoda.com/api/v1/video/vtoken/{0}?username=guest_{1}".format(username,randomid)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": self.url,
        }

        res = self.session.http.get(api_url, headers=headers,allow_redirects=True,verify=False)
        data = self.session.http.json(res, schema=self._data_schema)

        if not data:
            self.logger.info("Not a valid url.")
            return

        if data["status"] is False:
            self.logger.info("No username found. {0}".format(data["message"]))
            return

        self.author = username

        if len(data['edge_servers']) == 0:
            self.logger.info("Stream is currently offline or private")
            return

        if data["edge_servers"]:
            hls_url = "https://{0}/mp4:{1}_aac/playlist.m3u8?token={2}".format(data["edge_servers"][0],data["stream_name"],data["token"])

            if "edge" in data["edge_servers"][0]:
                self.session.http.verify = False
                self.session.http.headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0",
                    "Referer": self.url,
                    }

                hls_url = "https://{0}/{1}_v1/index.m3u8?token={2}".format(data["edge_servers"][0],data["stream_name"],data["token"])

            for s in HLSStream.parse_variant_playlist(self.session, hls_url).items():
                yield s

        return

__plugin__ = Camsoda
