import re

LINK_FINDER_RE = re.compile('\\"http://([^\\"]+)\\"')

def scanlinks(data):
    
    lsf = LINK_FINDER_RE.findall(data)
    links = []
        
    for i in lsf:
        print i
        if i.startswith("download.serienjunkies.org"):
            links.append('http://%s' % i)
        elif i.startswith("rapidshare.com"):
            links.append('http://%s' % i)
        
    return links
