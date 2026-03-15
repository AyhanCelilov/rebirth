import os
from urllib.parse import urlparse
import re

def _safe_filename(domain):
    parsed = urlparse(domain)
    base = parsed.netloc or domain
    return re.sub(r'[^A-Za-z0-9._-]+', '_', base)

def save_site(html_content, domain):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        folder = os.path.join(base_dir, "templates")
        filename = f"{_safe_filename(domain)}.html"
        path = os.path.join(folder, filename)

        with open(path, "w", encoding="utf-8") as f:
            f.write(html_content)
        return filename
    except TypeError:snapshot.html
    return "Error: could not generate filename for this site."

