import re
import uuid

from streamlink.plugin import Plugin
from streamlink.plugin.api import validate
from streamlink.stream.hls import HLSStream

_url_re = re.compile(r"https?://(\w+\.)?chaturbate\.com/(?P<username>\w+)")

class Chaturbate(Plugin):

    _data_schema = validate.Schema(
        {
            "room_status": validate.text,
            "room_title": validate.text,
            "broadcaster_username": validate.text,
            "broadcaster_gender": validate.text,
            "hls_source": validate.text,
        }
    )

    @classmethod
    def can_handle_url(cls, url):
        return _url_re.match(url)

    def get_title(self):
        return self.title

    def get_author(self):
        return self.author

    def get_category(self):
        return "NSFW LIVE"

    def _get_streams(self):
        match = _url_re.match(self.url)
        username = match.group("username")

        api_url = "https://chaturbate.com/api/chatvideocontext/{0}".format(username)
        CSRFToken = str(uuid.uuid4().hex.upper()[0:32])
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": CSRFToken,
            "X-Requested-With": "XMLHttpRequest",
            "Referer": self.url,
        }
        cookies = {
            "csrftoken": CSRFToken,
        }

        res = self.session.http.get(api_url, headers=headers, cookies=cookies)
        data = self.session.http.json(res, schema=self._data_schema)

        if not data:
            self.logger.info("Not a valid url.")
            return

        self.author = data["broadcaster_username"]
        self.title = data["room_title"]
        self.category = data["broadcaster_gender"]

        self.logger.info("Stream status: {0}".format(data["room_status"]))

        if (data["room_status"] == "public" and data["hls_source"]):
            for s in HLSStream.parse_variant_playlist(self.session, data["hls_source"]).items():
                yield s

__plugin__ = Chaturbate
