from .manifest import ManifestList


class Image:
    def __init__(self, client, manifest_list: ManifestList):
        self._client = client
        self.manifest_list = manifest_list
