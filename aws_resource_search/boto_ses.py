# -*- coding: utf-8 -*-

from boto_session_manager import BotoSesManager


class AWS:
    """
    .. note::

        since we use diskcache heavily, we put ``cache.memoize`` decorator on
        those methods that make boto3 API calls. It uses the instance and
        the argument all together to calculate the hash key for the cache.
        It actually firstly dump the object to pickle.

        However, the ``boto3.session.Session`` object is not hashable,
        no matter we put it as an attribute of the class, of we put it as an
        argument for each method, diskcache will raise an error anyway.

        So we have to declare a module level singleton object ``aws``, and
        use it for AWS credential.
    """
    def __init__(self):
        self.bsm: BotoSesManager

    def attach_bsm(self, bsm: BotoSesManager):
        self.bsm = bsm


aws = AWS()
