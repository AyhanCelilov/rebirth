def clean_domain_name(url):
    """Removes 'https://' , http:// and www. from a string to make it clean domain name"""
    clean_url = url.replace("https://","").replace("http://","").replace("www.","")
    return clean_url.split('/')[0].lower()

def format_timestamp(timestamp):
    if len(timestamp) >= 8 :
        year = timestamp[:4]
        month= timestamp[4:6]
        day = timestamp[6:8]
        return f"{day}-{month}-{day}"
    return "Unknown date"