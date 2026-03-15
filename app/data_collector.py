from datetime import datetime
import requests
from collections import defaultdict
#as we need multiple snapshots instead of 1, we use cdx instead of simple api
def fetch_archive(domain):
    api_url = f"http://web.archive.org/cdx/search/cdx?url={domain}&output=json&limit=100000&filter=statuscode:200"

    #we create empty snapshots array and add each snapshot to array by parsing it to year and month    
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
        #this is for displaying 1 snapshot per month otherwhise we should display more than a million snapshots which simple computer cannot handle
        limited_snapshots = []
        for month in sorted(per_month.keys(), reverse=True):  
            limited_snapshots.extend(per_month[month][:1])

        return limited_snapshots

    except Exception as e:
        print("Error fetching snapshots:", e)
        return []