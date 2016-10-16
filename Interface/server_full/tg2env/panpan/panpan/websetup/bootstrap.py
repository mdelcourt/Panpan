# -*- coding: utf-8 -*-
"""Setup the panpan application"""

import logging
from tg import config
from panpan import model
import transaction

def bootstrap(command, conf, vars):
    """Place any commands to setup panpan here"""

    # <websetup.bootstrap.before.auth

    # <websetup.bootstrap.after.auth>
