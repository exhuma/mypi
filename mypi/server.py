from os.path import join, exists
from os import makedirs

from flask import Flask, g, abort, render_template, send_from_directory
from werkzeug.utils import secure_filename

from mypi import db as model

app = Flask(__name__)

@app.before_request
def before_request():
    app.logger.debug("Before Request")
    g.db = model.Session()

@app.teardown_request
def teardown_request(exception):
    app.logger.debug("Teardown request")
    g.db.close()

@app.route("/", methods=['GET'])
@app.route("/project")
def hello():
    projects = model.Project.all(g.db)
    return render_template("project_list.html", projects=projects)

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

@app.route("/project/<author_email>/<name>")
def project(author_email, name):
    """
    Display the Project details
    """
    proj = model.Project.get(g.db, author_email, name)
    if not proj:
        abort(404, description = "No such project")

    return render_template("project.html", project=proj)

@app.route("/download/<project>/<md5>")
def download(project, md5):
    file = model.File.find(g.db, project, md5)
    if not file:
        return abort(404, description="File not found")

    folder = join(
            app.config['UPLOAD_FOLDER'],
            file.author_email.replace("@", "_at_"),
            project)

    return send_from_directory(
            folder, file.filename, as_attachment=True)

def _do_file_upload(data):
    from flask import request
    file = request.files['content']
    filename = secure_filename(file.filename)
    try:
        model.File.add(g.db, data, filename)
    except ValueError, exc:
        abort(409, description=str(exc))

    author_path = data['author_email'].replace('@', '_at_')
    target_dir = join(app.config["UPLOAD_FOLDER"], author_path, data['name'])
    if not exists(target_dir):
        makedirs(target_dir)
    file.save(join(target_dir, filename))
    app.logger.debug("File stored to %s" % join(target_dir, filename))
    g.db.commit()
    return "OK"

def _do_submit(data):
    app.logger.debug("Submitting a new packages")
    try:
        rel = model.Release.add(g.db, data)
        g.db.commit()
        return "added release %s" % rel
    except ValueError, ex:
        return abort(409, description=str(ex))


if __name__ == "__main__":
    app.run()
