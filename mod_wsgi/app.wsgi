#
# The following two lines are required if you are using a virtual-environment
#
activate_this = '/var/www/mypi/env/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from os.path import abspath, dirname
from os import getcwd, chdir
import logging, sys

from mypi.db import rebind
from mypi.server import app as application

# You may want to change this if you are using another logging setup
logging.basicConfig(stream=sys.stderr, level=logging.WARNING)

# This is important for SQLite. The database file will be stored in the
# current working folder. This line sets the working folder to the same folder
# as the WSGI script resides in. You may change this, if you know what you are
# doing.
chdir(abspath(dirname(__file__)))

LOG = logging.getLogger(__name__)
LOG.debug('Current path: {0}'.format(getcwd()))

# The database connection string. The database should be first initialised
# using sqlalchemy-migrate!
rebind('sqlite:///app.db', False)

# Application config
application.debug = False
application.config['UPLOAD_FOLDER'] = abspath('files')

# vim: set ft=python :
