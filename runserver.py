import logging

logging.basicConfig()
#logging.getLogger('sqlalchemy.engine').setLevel(logging.CRITICAL)

from mypi.db import rebind
from mypi.server import app

rebind('sqlite:///app.db', echo=True)

app.debug = True
app.run(host="0.0.0.0", port=8080)
