from typing import Optional


class Repository:
    def __init__(self, client, repository: str, namespace: Optional[str] = None):
        self._client = client
        self.repository: str = repository
        self.namespace: Optional[str] = namespace

        self._tags = None

    @property
    def name(self):
        if self.namespace:
            return "{self.namespace}/{self.repository}".format(self=self)
        return self.repository

    def tags(self):
        if self._tags is None:
            self.refresh()

        return self._tags

    def manifest(self, tag):
        """
        Return a tuple, (digest, manifest), for a given tag
        """
        return self._client.get_digest_and_manifest(self.name, tag)

    def delete_manifest(self, digest):
        return self._client.delete_manifest(self.name, digest)

    def refresh(self):
        response = self._client.get_repository_tags(self.name)
        self._tags = response["tags"]

    def __repr__(self):
        return "Repository({name})".format(name=self.name)


__all__ = (
    "Repository",
)
