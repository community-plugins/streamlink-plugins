import re
import json

from streamlink.plugin import Plugin, pluginmatcher
from streamlink.plugin.api import validate
from streamlink.stream import HLSStream, HTTPStream

_post_schema = validate.Schema({
        'data': validate.Schema({
            'getVideo': validate.Schema({
                'streamUrl' : validate.text,
                'directUrl' : validate.text,
                'title'  : validate.text,
                'channel': validate.Schema({
                    'title' : validate.text,
                })
            })
        })
})

@pluginmatcher(re.compile(
    r'https?://(?:www\.)?banned\.video/watch\?id=(?P<videoid>[0-f]{24})'
))

class BannedVideo(Plugin):

    _API_GRAPHQL='https://api.infowarsmedia.com/graphql'

    _GRAPHQL_GETMETADATA_QUERY='''
query GetVideoAndComments($id: String!) {
    getVideo(id: $id) {
        streamUrl
        directUrl
        title
        videoDuration
        channel {
            _id
            title
        }
        createdAt
    }
}
'''

    def _gql_persisted_query(self, id):
        return {
                'operationName': 'GetVideoAndComments',
                'variables': {'id': id},
                'query': self._GRAPHQL_GETMETADATA_QUERY
        }

    def get_title(self):
        return self.title

    def get_author(self):
        return self.author

    def get_category(self):
        return 'VOD'

    def _get_streams(self):
        videoid = self.match.group('videoid')

        post_data = self._gql_persisted_query(videoid)

        headers={ 'Content-Type': 'application/json; charset=utf-8' }

        res = self.session.http.post(self._API_GRAPHQL, headers=headers, data=json.dumps(post_data).encode('utf8'))
        data = self.session.http.json(res, schema=_post_schema)

        if not data:
            self.logger.info('Not a valid url.')
            return

        self.title = data['data']['getVideo']['title']
        self.author = data['data']['getVideo']['channel']['title']

        self.logger.info('Video: {0}'.format(self.title))

        if (data['data']['getVideo']['streamUrl']):
            for s in HLSStream.parse_variant_playlist(self.session, data['data']['getVideo']['streamUrl']).items():
                yield s

        if (data['data']['getVideo']['directUrl']):
            s = HTTPStream(self.session, data['data']['getVideo']['directUrl'])
            yield 'raw', s

__plugin__ = BannedVideo
