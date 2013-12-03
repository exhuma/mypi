import sys
import logging
import os
from os import getcwd

logging.basicConfig(stream=sys.stderr, level=logging.WARNING)

LOG = logging.getLogger(__name__)
LOG.debug('Current path: {0}'.format(getcwd()))

from mypi.db import rebind
from mypi.server import app as application

application.debug = False

rebind(os.environ['DATABASE_URL'], False)
