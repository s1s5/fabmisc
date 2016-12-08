# coding: utf-8
def expand_config(_env, d):
    def _set_env(d, parent=None):
        if isinstance(d, dict):
            for key, value in d.items():
                if parent is not None:
                    key = parent + '_' + key
                if isinstance(value, dict):
                    _set_env(value, key)
                else:
                    _env[key] = value
        elif isinstance(d, list):
            for i in d:
                _set_env(i, parent)
    _set_env(d)


def extract_children_keys(d):
    s = set()

    def _set_env(d):
        if isinstance(d, list):
            for i in d:
                _set_env(d)
        if isinstance(d, dict):
            for key, value in d.items():
                if isinstance(value, dict):
                    _set_env(value)
                else:
                    s.add(key.upper())
    _set_env(d)
    return s
