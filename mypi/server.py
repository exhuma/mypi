from os.path import join
from os import makedirs

from flask import Flask, g, abort
from werkzeug.utils import secure_filename

from mypi import db as model

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = "files"

@app.before_request
def before_request():
    app.logger.debug("Before Request")
    g.db = model.Session()


@app.teardown_request
def teardown_request(exception):
    app.logger.debug("Teardown request")
    g.db.close()


@app.route("/", methods=['GET'])
def hello():
    model.User.by_auth(g.db, '', '')
    return "Hello World!"


@app.route("/", methods=['POST'])
def post():
    from flask import request
    frm = request.form

    action_name = "_do_%s" % frm[":action"]
    app.logger.debug("Performing %s" % action_name)
    action = globals().get(action_name, None)
    if action:
        return action(frm)

    return abort(501, description="Action %s is not yet implemented" % frm[":action"])

def _do_file_upload(data):
    from flask import request
    file = request.files['content']
    filename = secure_filename(file.filename)
    try:
        model.File.add_meta(g.db, data)
        author_path = data['author_email'].replace('@', '_at_')
        target_dir = join(app.config.get("UPLOAD_FOLDER", "files"), author_path, data['name'])
        makedirs(target_dir)
        file.save(join(target_dir, filename))
        app.logger.debug("File stored to %s" % join(target_dir, filename))
        g.db.commit()
    except Exception, exc:
        app.logger.error(exc)
        g.db.rollback()
    return "OK"

def _do_submit(data):
    app.logger.debug("Submitting a new packages")
    try:
        rel = model.Release.add(g.db, data)
        return "added release %s" % rel
    except ValueError, ex:
        return abort(409, description=str(ex))


if __name__ == "__main__":
    app.run()
