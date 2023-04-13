import re
import uuid

from streamlink.plugin import Plugin, pluginmatcher
from streamlink.plugin.api import validate
from streamlink.stream.hls import HLSStream
from streamlink.exceptions import PluginError

@pluginmatcher(re.compile(
    r"https?://(\w+\.)?chaturbate\.com/(?P<username>\w+)"
))

class Chaturbate(Plugin):

    _data_schema = validate.Schema({
        "room_status": str,
        "room_title": str,
        "broadcaster_username": str,
        "broadcaster_gender": str,
        "hls_source": str,
    })

    def get_title(self):
        return self.title

    def get_author(self):
        return self.author

    def get_category(self):
        return "NSFW LIVE"

    def _get_streams(self):
        username = self.match.group("username")

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

        try:
            res = self.session.http.get(api_url, headers=headers, cookies=cookies)
        except PluginError:
            try:
                self.logger.info("using cloudscraper")
                import cloudscraper
                res = cloudscraper.create_scraper().get(api_url, headers=headers)
            except (PluginError, TypeError) as err:
                self.logger.debug(err)

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
