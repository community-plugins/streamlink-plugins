import re
import uuid

from streamlink.plugin import Plugin, pluginmatcher
from streamlink.plugin.api import validate
from streamlink.stream import HLSStream

API_HLS = "https://chaturbate.com/get_edge_hls_url_ajax/"

_post_schema = validate.Schema(
    {
        "url": validate.text,
        "room_status": validate.text,
        "success": int
    }
)

@pluginmatcher(re.compile(
    r"https?://(\w+\.)?chaturbate\.com/(?P<username>\w+)"
))

class Chaturbate(Plugin):

    def get_title(self):
        return self.author

    def get_author(self):
        return self.author

    def get_category(self):
        return "Live"

    def _get_streams(self):
        username = self.match.group("username")

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

        post_data = "room_slug={0}&bandwidth=high".format(username)

        res = self.session.http.post(API_HLS, headers=headers, cookies=cookies, data=post_data)
        data = self.session.http.json(res, schema=_post_schema)

        if not data:
            self.logger.info("Not a valid url.")
            return

        self.author = username

        self.logger.info("Stream status: {0}".format(data["room_status"]))

        if (data["success"] is True and data["room_status"] == "public" and data["url"]):
            for s in HLSStream.parse_variant_playlist(self.session, data["url"]).items():
                yield s

__plugin__ = Chaturbate
