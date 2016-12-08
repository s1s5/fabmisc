# coding: utf-8
import os

from fabric.contrib.files import upload_template

from .managed_task import ManagedTask
from .utility import recv_lazy


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')


class EnvVars(ManagedTask):
    def __init__(self, filename, prefix, keys, dictionary, *args, **kw):
        super(EnvVars, self).__init__(*args, **kw)
        self.filename = recv_lazy(filename, (str, unicode))
        self.prefix = recv_lazy(prefix, (str, unicode))
        self.keys = recv_lazy(keys)
        self.dictionary = recv_lazy(dictionary)

    def run(self):
        items = []
        for i in self.keys():
            items.append((i, self.dictionary()[i]))

        upload_template(
            'env_vars.sh', '~/.env_vars/{}'.format(self.filename()),
            context=dict(
                prefix=self.prefix(),
                items=items,
            ),
            template_dir=TEMPLATE_DIR, use_jinja=True, mode='0600')
