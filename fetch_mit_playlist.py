import json
from yt_dlp import YoutubeDL
url='https://www.youtube.com/playlist?list=PLUl4u3cNGP601Q2jo-J_3raNCMMs6Jves'
with YoutubeDL({'extract_flat': True, 'quiet': True, 'ignoreerrors': True}) as ydl:
    info=ydl.extract_info(url, download=False)
open('mit_18_642_playlist.json','w',encoding='utf-8').write(json.dumps(info,ensure_ascii=False,indent=2))
print(info.get('title'), len(info.get('entries') or []))
for i,e in enumerate(info.get('entries') or [],1):
    print(i,e.get('id'),e.get('title'))
