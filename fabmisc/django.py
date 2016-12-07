# coding: utf-8
from __future__ import absolute_import

import sys
import os


def settings(filepath, proj_name):
    sys.path.append(os.path.join(
        os.path.dirname(os.path.abspath(filepath)), proj_name))
    from fabric.contrib.django import settings_module   # NOQA
    settings_module('settings')
    from django.conf import settings as djsettings   # NOQA
    return djsettings
