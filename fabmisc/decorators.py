# coding: utf-8
from fabric.decorators import task


def load_config_task(_func):
    def func(*args, **kw):
        from fabric.state import env
        env['_initialized'] = True
        return _func(*args, **kw)
    func.__name__ = _func.__name__
    return task(func)


def config_required_task(_func):
    def func(*args, **kw):
        from fabric.state import env
        if not env.get('_initialized'):
            raise Exception("You must load config to "
                            "execute task '{}'".format(_func.__name__))
        return _func(*args, **kw)
    func.__name__ = _func.__name__
    return task(func)
