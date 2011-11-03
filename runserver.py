from mypi.db import rebind
from mypi.server import app
from os.path import abspath

rebind('sqlite:///app.db', True)

app.debug = True
app.config['UPLOAD_FOLDER'] = abspath('files')
app.run(host="0.0.0.0", port=8080)
