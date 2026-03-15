
import os
import re6
import requests
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
import time
from extensions import db
from models import SearchLog
from resurrect import save_site
from llm import archieveAnalyse, nostalgic_recommendations
from data_collector import fetch_archive

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.root_path, "app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    db.create_all()



_nostalgic_cache = {
    "ts": 0.0,
    "data": None,
}

#looking for most used 6 sites in the last 10 years and displays it in the main page
@app.get('/nostalgic')
def nostalgic():
    years_ago = request.args.get('years_ago', '10')
    count = request.args.get('count', '6')

    try:
        years_ago_i = max(1, min(30, int(years_ago)))
    except Exception:
        years_ago_i = 10

    try:
        count_i = max(3, min(12, int(count)))
    except Exception:
        count_i = 6

    now = time.time()
    ttl_seconds = 60 * 60
    if _nostalgic_cache["data"] is not None and (now - float(_nostalgic_cache["ts"])) < ttl_seconds:
        return jsonify(_nostalgic_cache["data"])

    data = nostalgic_recommendations(years_ago=years_ago_i, count=count_i)
    _nostalgic_cache["ts"] = now
    _nostalgic_cache["data"] = data
    return jsonify(data)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == "GET":
        return render_template("home.html")

    domain = request.form.get("rebirthURL")
    from data_collector import fetch_archive
    snapshots = fetch_archive(domain)
    return render_template("snapshots.html", snapshots=snapshots, domain=domain)

@app.route('/load_snapshot', methods=['POST'])
def load_snapshot():
    combined_data = request.form.get("snapshot", "")
    try:
        url, date = combined_data.split("|", 1) if "|" in combined_data else (combined_data, "Unknown")
    except:
        return "Selection Error", 400


    if "/web/" in url:
        url = re.sub(r"/web/(\d+)/", r"/web/\1oe_/", url)

    db.session.add(SearchLog(url=url, date=date))
    db.session.commit()

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=30)
        html = response.text

        match = re.search(r"(https://web\.archive\.org/web/\d+oe_/http[^/]*)/?", url)
        if match:
            base_url = match.group(1) + "/"
            base_tag = f'''
            <base href="{base_url}">
            <meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests">
            '''
            
            if "<head>" in html:
                html = html.replace("<head>", f"<head>{base_tag}")
            else:
                html = base_tag + html

        # 4. Save and send
        save_site(html, "snapshot")
        return send_file(os.path.join(app.root_path, "templates", "snapshot.html"))

    except Exception as e:
        print(f"Error: {e}")
        return f"Failed to restore original design: {str(e)}", 500
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


@app.route("/get_info", methods=["POST"])
def get_info():
    try:
        data = request.get_json(silent=True) or {}
        timestamp = (data.get('date') or '').strip()
        website_url = (data.get('website') or '').strip()

        if not timestamp or not website_url:
            return jsonify({"error": "Missing 'website' or 'date'."}), 400

        response = archieveAnalyse(website_url, timestamp)

        if isinstance(response, dict):
            return jsonify(response)

        return jsonify({
            "summary": str(response),
            "design_notes": [],
            "context_of_the_time": "",
            "impact": "",
        })
    except Exception as e:
        print(f"Error during IA analyse: {e}")
        return jsonify({"error": "Error during IA analyse!"}), 500


#if domain is not missing, bring chosen snpshot's timestamp
@app.route('/best_snapshot', methods=['POST'])
def best_snapshot():
    domain = request.form.get("domain")
    if not domain:
        return "Domain missing", 400

    snapshots = fetch_archive(domain)
    if not snapshots:
        return render_template("snapshots.html", snapshots=[], domain=domain, best_timestamp=None, message="No snapshots found")

    best_snapshot = None
    max_size = 0

    for s in snapshots:  
        url = s.get("url")
        ts = s.get("timestamp")
        if not url:
            continue
        try:
            html = requests.get(url, timeout=5).text
            size = len(html)
            if size > max_size:
                max_size = size
                best_snapshot = {"url": url, "timestamp": ts, "size": size}
        except requests.RequestException:
            continue
 # best is the longest one
    if not best_snapshot:
        return render_template("snapshots.html", snapshots=snapshots, domain=domain, best_timestamp=None, message="No valid snapshot found")

    # Pass only the timestamp to the template
    return render_template(
        "snapshots.html",
        snapshots=snapshots,
        domain=domain,
        best_timestamp=best_snapshot["timestamp"],
        message=None
    )
if __name__ == "__main__":
    app.run(debug=True) 