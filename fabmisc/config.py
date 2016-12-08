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
                    if key in _env:
                        raise AttributeError(
                            "key '{}' already exists".format(key))
                    _env[key] = value
    _set_env(d)
