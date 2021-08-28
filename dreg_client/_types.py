from __future__ import annotations

from typing import Callable, Tuple, Union

from requests import PreparedRequest


RequestsAuth = Union[None, Callable[[PreparedRequest], PreparedRequest], Tuple[str, str]]
