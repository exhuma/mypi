from mypi.db import rebind
from mypi.server import app

rebind('sqlite:///app.db', True)

app.debug = True
app.run(host="0.0.0.0", port=8080)
