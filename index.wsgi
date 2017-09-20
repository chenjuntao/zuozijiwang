# -*- coding: utf-8 -*-

import os

import sae

from bottle import default_app, debug

import main

debug(True)

os.chdir(os.path.dirname(__file__))
app = default_app()
application = sae.create_wsgi_app(app)