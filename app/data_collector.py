from datetime import datetime
import requests
from collections import defaultdict

def fetch_archive(domain):
    api_url = f"http://web.archive.org/cdx/search/cdx?url={domain}&output=json&limit=100000&filter=statuscode:200"

    try:
        response = requests.get(api_url).json()
        snapshots = []
        per_month = defaultdict(list)

        for row in response[1:]:  
            timestamp = row[1]
            dt = datetime.strptime(timestamp, "%Y%m%d%H%M%S")
            month_key = dt.strftime("%Y-%m")  

            snapshot_url = f"https://web.archive.org/web/{timestamp}/{domain}"

            per_month[month_key].append({
                "timestamp": dt.strftime("%d %b %Y"),
                "url": snapshot_url
            })

        limited_snapshots = []
        for month in sorted(per_month.keys(), reverse=True):  
            limited_snapshots.extend(per_month[month][:1])

        return limited_snapshots

    except Exception as e:
        print("Error fetching snapshots:", e)
        return []