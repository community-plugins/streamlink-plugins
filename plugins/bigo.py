import re

from streamlink.plugin import Plugin, pluginmatcher
from streamlink.plugin.api import useragents, validate
from streamlink.stream import HLSStream

@pluginmatcher(re.compile(
    r"https?://(?:www\.)?bigo\.tv/([^/]+)$"
))
class Bigo(Plugin):
    _api_url = "https://bigo.tv/studio/getInternalStudioInfo?siteId={0}"

    _post_schema = validate.Schema({
        "code": int,
        "msg": str,
        "data": validate.any({
            "nick_name": validate.text,
            "roomTopic": validate.text,
            "gameTitle": validate.text,
            "alive": int,
            validate.optional("hls_src"): validate.url(),

        },[])
    })

    def get_title(self):
        return self.title

    def get_author(self):
        return self.author

    def get_category(self):
        return self.category

    def _get_streams(self):
        res = self.session.http.get(
            self._api_url.format(self.match.group(1)),
            allow_redirects=True,
            headers={"User-Agent": useragents.IPHONE_6}
        )
        data = self.session.http.json(res, schema=self._post_schema)

        if not data:
            self.logger.info("Not a valid url.")
            return

        if data["code"] != 0:
            self.logger.info('getInternalStudioInfo returns code "{0}", msg "{1}"'.format(data["code"],data["msg"]))
            return

        if data["data"]['alive'] == 0:
            self.logger.info('User "{0}" is not live at the moment'.format(self.match.group(1)))
            return

        self.author = data["data"]["nick_name"]
        self.title = data["data"]["roomTopic"]
        self.category = data["data"]["gameTitle"]

        videourl = data["data"]["hls_src"]
        if videourl:
            yield "live", HLSStream(self.session, videourl)


__plugin__ = Bigo
