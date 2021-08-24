import dataclasses


@dataclasses.dataclass(frozen=True)
class Manifest:
    content: dict
    content_type: str
    digest: str


__all__ = ("Manifest",)
