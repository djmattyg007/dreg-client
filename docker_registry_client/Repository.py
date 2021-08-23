class BaseRepository(object):
    def __init__(self, client, repository, namespace=None):
        self._client = client
        self.repository = repository
        self.namespace = namespace

    @property
    def name(self):
        if self.namespace:
            return "{self.namespace}/{self.repository}".format(self=self)
        return self.repository


class RepositoryV2(BaseRepository):
    def __init__(self, client, repository, namespace=None):
        super(RepositoryV2, self).__init__(client, repository,
                                           namespace=namespace)
        self._tags = None

    def __repr__(self):
        return 'RepositoryV2({name})'.format(name=self.name)

    def tags(self):
        if self._tags is None:
            self.refresh()

        return self._tags

    def manifest(self, tag):
        """
        Return a tuple, (manifest, digest), for a given tag
        """
        return self._client.get_manifest_and_digest(self.name, tag)

    def delete_manifest(self, digest):
        return self._client.delete_manifest(self.name, digest)

    def refresh(self):
        response = self._client.get_repository_tags(self.name)
        self._tags = response['tags']


def Repository(client, *args, **kwargs):
    return RepositoryV2(client, *args, **kwargs)
