# coding: utf-8
from .utility import lazy_property


class TableMixin(object):
    table = lazy_property((str, unicode))
    user = lazy_property((str, unicode))
    password = lazy_property((str, unicode))
    hostname = lazy_property((str, unicode))

    def __init__(self, table, user=None,
                 password=None, hostname='127.0.0.1', **kw):
        super(TableMixin, self).__init__(**kw)
        self.table = table
        self.user = user
        self.password = password
        self.hostname = hostname
