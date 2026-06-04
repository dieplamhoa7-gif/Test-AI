import json, re
from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi
pl=json.loads(Path('mit_18_642_playlist.json').read_text(encoding='utf-8'))
out=Path('mit_18_642_transcripts'); out.mkdir(exist_ok=True)
summary=[]
for i,e in enumerate(pl.get('entries') or [],1):
    vid=e.get('id'); title=e.get('title') or ''
    print(i, vid, title, flush=True)
    rec={'index':i,'id':vid,'title':title,'ok':False,'error':None,'path':None}
    try:
        ytt=YouTubeTranscriptApi()
        fetched=ytt.fetch(vid, languages=['en','en-US'])
        rows=[{'start':x.start,'duration':x.duration,'text':x.text} for x in fetched]
        text=' '.join(re.sub(r'\s+',' ',r['text']).strip() for r in rows)
        p=out/f'{i:02d}_{vid}.json'
        p.write_text(json.dumps({'index':i,'id':vid,'title':title,'rows':rows,'text':text},ensure_ascii=False,indent=2),encoding='utf-8')
        rec.update(ok=True,path=str(p),chars=len(text))
    except Exception as ex:
        rec['error']=type(ex).__name__+': '+str(ex)[:500]
    summary.append(rec)
Path('mit_18_642_transcripts_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print('done', sum(1 for r in summary if r['ok']), '/', len(summary))
