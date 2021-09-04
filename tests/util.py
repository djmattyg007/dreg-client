import functools
import inspect
from contextlib import contextmanager
from typing import Generator
from unittest import mock


@contextmanager
def spy(obj: object, name: str) -> Generator[mock.MagicMock, None, None]:
    method = getattr(obj, name)
    autospec = inspect.ismethod(method) or inspect.isfunction(method)

    def wrapper(*args, **kwargs):
        spy_obj.spy_return = None
        spy_obj.spy_exception = None
        try:
            retval = method(*args, **kwargs)
        except BaseException as e:
            spy_obj.spy_exception = e
            raise
        else:
            spy_obj.spy_return = retval
        return retval

    wrapped = functools.update_wrapper(wrapper, method)

    with mock.patch.object(obj, name, side_effect=wrapped, autospec=autospec) as spy_obj:
        spy_obj.spy_return = None
        spy_obj.spy_exception = None
        yield spy_obj
