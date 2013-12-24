from __future__ import print_function
import logging

from flask import Blueprint, current_app
from flask import g, abort, render_template, request
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename

from mypi.core import App


LOG = logging.getLogger(__name__)
CORE = Blueprint('core', __name__)


@CORE.before_request
def before_request():
    """
    Make the DB accessible for each request.
    """

    url = current_app._mypi_conf.get('sqlalchemy', 'url')
    sess = current_app._session or scoped_session(sessionmaker(url))()
    g.db = sess
    # Rename this "app" to "mypi" to distinguish it better from the flask app!
    g.app = App(sess)


@CORE.teardown_request
def teardown_request(exception):
    """
    Close the DB connection after each request.
    """
    g.db.close()


@CORE.route("/", methods=['GET'])
@CORE.route("/package/")
def index():
    """
    Main index page.
    """
    packages = g.app.get_package_list()
    return render_template("package_list.html", packages=packages)


@CORE.route("/", methods=['POST'])
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


@CORE.route("/<name>/")
@CORE.route("/package/<name>/")
def package(name):
    """
    Display the Package details
    """
    proj = g.app.get_package_by_name(name)
    if not proj:
        return abort(404, description="No such package")

    return render_template("package.html", package=proj)


@CORE.route("/download/<pkg>/<filename>/")
def download(pkg, filename):
    """
    Handle package downloads.
    """
    file_ = g.app.package_file_by_filename(pkg, filename)
    if not file_:
        return abort(404, description="File not found")

    from werkzeug.wrappers import Response
    resp = Response(file_.data)
    resp.headers['Content-Type'] = 'application/x-gzip'
    resp.headers['Content-Disposition'] = (
        'attachement; filename="%s"' % filename)

    return resp


@CORE.route("/simple/")
def simple():
    """
    List all available packages
    """
    packages = g.app.get_package_list()
    return render_template("simple/packages.html", packages=packages)


@CORE.route("/simple/<pkg>")
@CORE.route("/simple/<pkg>/")
def simple_package(pkg):
    """
    List all available package releases.
    """
    pkg = g.app.get_package_by_name(pkg)
    if not pkg:
        abort(404, description="No such package")
    return render_template("simple/releases.html", package=pkg)


def _do_file_upload(data):
    """
    Store the file in the database.
    """
    file_ = request.files['content']
    filename = secure_filename(file_.filename)

    g.app.upload(data, filename, file_.stream)

    try:
        g.db.commit()
    except IntegrityError, exc:
        LOG.error(exc)
        abort(409, description="This file exists already!")

    return "OK"


def _do_submit(data):
    """
    Stores a package submission in the database.
    """
    try:
        rel = g.app.register_release(data)
        g.db.commit()
        return "added release %s" % rel
    except ValueError, ex:
        return abort(409, description=str(ex))


