
class MultiClientService(object):
    @property
    def api_client(self):
        return self._api_client or get_api_client()

    def with_api_client(self, api_client):
        #TODO
