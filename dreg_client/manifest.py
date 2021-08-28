from __future__ import annotations

import dataclasses


@dataclasses.dataclass(frozen=True)
class Manifest:
    digest: str
    content_type: str
    content: dict = dataclasses.field(compare=False)


__all__ = ("Manifest",)
