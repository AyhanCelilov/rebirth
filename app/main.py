import os
import requests
from data_collector import fetch_archive
from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from extensions import db
from models import SearchLog
from resurrect import save_site

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.root_path, "app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == "GET":
        return render_template("home.html")
    
    domain = request.form["rebirthURL"]
    snapshots = fetch_archive(domain)
    return render_template("snapshots.html", snapshots=snapshots, domain=domain)

@app.route('/load_snapshot', methods=['POST'])
def load_snapshot():
    combined_data = request.form.get("snapshot", "")

    # Expected format from snapshots.html: "<wayback_url>|<human_date>"
    if "|" in combined_data:
        snapshot_url, snapshot_date = combined_data.split("|", 1)
    else:
        snapshot_url = combined_data
        snapshot_date = "Unknown Date"

    snapshot_url = (snapshot_url or "").strip()
    print("Loading snapshot:", snapshot_url, "(" + snapshot_date + ")")

    # Prefer the raw capture (no Wayback toolbar): /web/<ts>id_/<url>
    # If it's already id_/im_/js_/cs_ etc, leave it alone.
    if "/web/" in snapshot_url and "id_/" not in snapshot_url:
        snapshot_url = snapshot_url.replace("/web/", "/web/")
        # Insert id_ after the timestamp segment if missing.
        # Example: /web/20060303/https://example.com -> /web/20060303id_/https://example.com
        snapshot_url = snapshot_url.replace("/web/", "/web/", 1)
        # Only transform URLs of the form .../web/<digits>/...
        import re
        snapshot_url = re.sub(r"/web/(\d{6,14})/", r"/web/\1id_/", snapshot_url, count=1)


    log = SearchLog(url=snapshot_url, date=snapshot_date)
    db.session.add(log)
    db.session.commit()

    html = requests.get(snapshot_url, timeout=25).text
    save_site(html, "snapshot")
    path = os.path.join(app.root_path, "templates", "snapshot.html")
    return send_file(path)

@app.route('/history', methods=['GET', 'POST'])
def history():
    search_logs = SearchLog.query.all()
    return render_template("history.html", search_logs=search_logs)

@app.route('/history/delete/<int:search_id>', methods=['GET', 'POST'])
def delete_search_log(search_id):
    search = SearchLog.query.get_or_404(search_id)
    db.session.delete(search)
    db.session.commit()
    flash(f"Search deleted successfully.")
    return redirect(url_for('history'))

if __name__ == "__main__":
    app.run(debug=True)