from flask import Flask, g, abort

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
    return abort(501, description="File upload not yet implemented")

def _do_submit(data):
    app.logger.debug("Submitting a new packages")
    try:
        rel = model.Release.add(g.db, data)
        return "added release %s" % rel
    except ValueError, ex:
        return abort(409, description=str(ex))


if __name__ == "__main__":
    app.run()
