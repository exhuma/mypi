"""
Main web application code.
"""
from __future__ import print_function
import logging
from sqlalchemy.orm import sessionmaker, scoped_session

from flask import Flask, g, abort, render_template, request
from werkzeug.utils import secure_filename

from mypi.manager import Manager

LOG = logging.getLogger(__name__)
APP = Flask(__name__)


@APP.before_request
def before_request():
    """
    Make the DB accessible for each request.
    """
    g.config = APP.config['ini']
    sess = scoped_session(sessionmaker(g.config.get('sqlalchemy', 'url')))
    g.db = sess()
    g.manager = Manager(g.db)


@APP.teardown_request
def teardown_request(exception):
    """
    Close the DB connection after each request.
    """
    g.db.close()


@APP.route("/", methods=['GET'])
@APP.route("/package/")
def index():
    """
    Main index page.
    """
    packages = model.Package.all(g.db)
    return render_template("package_list.html", packages=packages)


@APP.route("/", methods=['POST'])
def post():
    """
    Handle POST requests to the web root.
    """
    frm = request.form

    action_name = "_do_%s" % frm[":action"]
    action = globals().get(action_name, None)
    if action:
        return action(frm)

    LOG.error('Attempted to executed unimplemented action: %s', action_name)
    return abort(501, description=(
        "Action %s is not yet implemented" % frm[":action"]))


@APP.route("/<name>/")
@APP.route("/package/<name>/")
def package(name):
    """
    Display the Package details
    """
    proj = model.Package.get(g.db, name)
    if not proj:
        return abort(404, description="No such package")

    return render_template("package.html", package=proj)


@APP.route("/download/<pkg>/<filename>/")
def download(pkg, filename):
    """
    Handle package downloads.
    """
    file_ = model.File.find_by_filename(g.db, pkg, filename)
    if not file_:
        return abort(404, description="File not found")

    from werkzeug.wrappers import Response
    resp = Response(file_.data)
    resp.headers['Content-Type'] = 'application/x-gzip'
    resp.headers['Content-Disposition'] = (
        'attachement; filename="%s"' % filename)

    return resp


@APP.route("/simple/")
def simple():
    """
    List all available packages
    """
    packages = model.Package.all(g.db)
    return render_template("simple/packages.html", packages=packages)


@APP.route("/simple/<pkg>")
@APP.route("/simple/<pkg>/")
def simple_package(pkg):
    """
    List all available package releases.
    """
    pkg = model.Package.get(g.db, pkg)
    if not pkg:
        abort(404, description="No such package")
    return render_template("simple/releases.html", package=pkg)


def _do_file_upload(data):
    """
    Store the file in the database.
    """
    file_ = request.files['content']
    filename = secure_filename(file_.filename)

    model.File.upload(g.db, data, filename, file_.stream)

    try:
        g.db.commit()
    except model.IntegrityError, exc:
        LOG.error(exc)
        abort(409, description="This file exists already!")
    return "OK"


def _do_submit(data):
    """
    Stores a package submission in the database.
    """
    try:
        rel = model.Release.register(g.db, data)
        g.db.commit()
        return "added release %s" % rel
    except ValueError, ex:
        return abort(409, description=str(ex))


if __name__ == "__main__":
    print(">>> Running DEVELOPMENT server!")
    APP.run(host='0.0.0.0', debug=True)
