import logging

from flask import Flask, g, abort, render_template
from werkzeug.utils import secure_filename

from mypi import db as model

LOG = logging.getLogger(__name__)
app = Flask(__name__)

@app.before_request
def before_request():
    g.db = model.Session()

@app.teardown_request
def teardown_request(exception):
    g.db.close()

@app.route("/", methods=['GET'])
@app.route("/package/")
def index():
    packages = model.Package.all(g.db)
    return render_template("package_list.html", packages=packages)

@app.route("/", methods=['POST'])
def post():
    from flask import request
    frm = request.form

    #TODO: raise error if :action not in frm
    action_name = "_do_%s" % frm[":action"]
    action = globals().get(action_name, None)
    if action:
        return action(frm)

    return abort(501, description="Action %s is not yet implemented" % frm[":action"])

@app.route("/package/<name>/")
def package(name):
    """
    Display the Package details
    """
    proj = model.Package.get(g.db, name)
    if not proj:
        return abort(404, description = "No such package")

    return render_template("package.html", package=proj)

@app.route("/download/<package>/<filename>/")
def download(package, filename):
    file = model.File.find_by_filename(g.db, package, filename)
    if not file:
        return abort(404, description="File not found")

    from werkzeug.wrappers import Response
    resp = Response(file.data)
    resp.headers['Content-Type'] = 'application/octet-stream'
    resp.headers['Content-Disposition'] = 'attachement'

    return resp

@app.route("/simple/")
def simple():
    """
    List all available packages
    """
    packages = model.Package.all(g.db)
    return render_template("simple/packages.html", packages=packages)

@app.route("/simple/<package>")
@app.route("/simple/<package>/")
def simple_package(package):
    """
    List all available package releases
    """
    package = model.Package.get(g.db, package)
    if not package:
        abort(404, description = "No such package")
    return render_template("simple/releases.html", package=package)

def _do_file_upload(data):
    from flask import request
    file = request.files['content']
    filename = secure_filename(file.filename)

    model.File.upload(g.db, data, filename, file.stream)

    try:
        g.db.commit()
    except model.IntegrityError, exc:
        LOG.error(exc)
        abort(409, description="This file exists already!")
    return "OK"

def _do_submit(data):
    try:
        rel = model.Release.register(g.db, data)
        g.db.commit()
        return "added release %s" % rel
    except ValueError, ex:
        return abort(409, description=str(ex))


if __name__ == "__main__":
    app.run()
