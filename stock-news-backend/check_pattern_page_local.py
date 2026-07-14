import urllib.request
r=urllib.request.urlopen('http://127.0.0.1:8123/pattern-reco.html?ts=enginelevels',timeout=5)
h=r.read().decode('utf-8')
print(r.status, len(h), 'addEngineOverlay' in h, 'level-chip' in h)
