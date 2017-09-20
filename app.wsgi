
import os, sys

sys.path=['/var/www/zuoziji/'] + sys.path
print sys.path
os.chdir(os.path.dirname(os.path.abspath(__file__)))
#os.chdir('/var/www/zuoziji/')

import main
import bottle

print('WSGI Server has started.............................')

application = bottle.default_app()