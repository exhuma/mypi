from flask import Flask
app = Flask(__name__)

PACKAGES = {}

@app.route("/", methods=['GET'])
def hello():
    return "Hello World!"


@app.route("/", methods=['POST'])
def post():
    from flask import request
    frm = request.form
    PACKAGES.setdefault(frm['name'], [])
    PACKAGES[frm['name']].append((
        frm["license"],
        frm["name"],
        frm["metadata_version"],
        frm["author"],
        frm["home_page"],
        frm[":action"],
        frm["download_url"],
        frm["summary"],
        frm["author_email"],
        frm["version"],
        frm["platform"],
        frm["description"]
    ))
    #TODO: Avoid duplicates (return error if name/version conflict)
    import pdb; pdb.set_trace()
    return "OK"

if __name__ == "__main__":
    app.run()
