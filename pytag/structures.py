import collections

from pytag.constants import FIELD_NAMES


class CaseInsensitiveDict(collections.MutableMapping):
    """A case-insensitive :py:class:`dict`-like object.

    Implements all methods and operations of
    :py:class:`collections.abc.MutableMapping` as well as dict's
    :py:meth:`dict.copy`.

    All keys are expected to be strings. The structure always set the key to
    lower case.

    ::

        cid = CaseInsensitiveDict()
        cid['Key'] = 'value'
        cid['KEY'] == 'value'  # True
        list(cid) == ['key']   # True

    If the constructor, update, or equality comparison operations are given
    keys that have equal :py:meth:`str.lower`, the behavior is undefined.
    """

    def __init__(self, data=None, **kwargs):
        self._store = dict()
        if data is None:
            data = {}
        self.update(data, **kwargs)

    def __setitem__(self, key, value):
        self._store[key.lower()] = value

    def __getitem__(self, key):
        return self._store[key.lower()]

    def __delitem__(self, key):
        del self._store[key.lower()]

    def __iter__(self):
        return (key for key in self._store)

    def __len__(self):
        return len(self._store)

    def __eq__(self, other):
        return other == self._store

    def copy(self):
        return CaseInsensitiveDict(self._store)

    def __repr__(self):    # pragma: no cover
        return '{}({})'.format(self.__class__.__name__, self._store)


class PytagDict(CaseInsensitiveDict):
    """ A case-insensitive :py:class:`dict`-like object where only the values
    defines in :py:data:`pytag.constants.FIELD_NAMES` constant are allowed as
    keys. If a key is not valid, is ignored without any warning.
    """

    def __setitem__(self, key, value):
        key = key.lower()
        if key in FIELD_NAMES:
            self._store[key] = value
