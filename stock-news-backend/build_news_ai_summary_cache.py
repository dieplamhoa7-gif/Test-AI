from __future__ import annotations
import json, re
from pathlib import Path
from datetime import datetime, timezone, timedelta
ROOT=Path(__file__).resolve().parent
TZ=timezone(timedelta(hours=7))
FILES=[ROOT/'data'/'news_cache.json', ROOT/'firebase_public'/'data'/'news_cache.json']
EN_FILES=[ROOT/'data'/'news_cache_en.json', ROOT/'firebase_public'/'data'/'news_cache_en.json']

KEYWORDS={
 'stock':['cổ phiếu','chứng khoán','vn-index','vnindex','thị trường','ctck','thanh khoản','nhà đầu tư'],
 'business':['lợi nhuận','doanh thu','kế hoạch','cổ tức','phát hành','trái phiếu','tài chính'],
 'macro':['lãi suất','tỷ giá','ngân hàng','evn','chính sách','xuất khẩu','bất động sản','đầu tư công']
}

def clean(s):
    return re.sub(r'\s+',' ',str(s or '')).strip()

def split_sent(text):
    text=clean(text)
    parts=re.split(r'(?<=[.!?。])\s+|(?<=\.)\s+|(?<=\?)\s+|(?<=!)\s+',text)
    out=[]
    for p in parts:
        p=clean(p)
        if len(p)>=25 and p not in out: out.append(p)
    return out

def classify(text):
    low=text.lower(); hits=[]
    for k,words in KEYWORDS.items():
        sc=sum(1 for w in words if w in low)
        if sc: hits.append((sc,k))
    return max(hits)[1] if hits else 'market'

def make_summary(item):
    title=clean(item.get('title'))
    snippet=clean(item.get('snippet') or item.get('summary') or item.get('description'))
    content=clean(item.get('fullText') or item.get('content') or item.get('body') or item.get('text'))
    source_text=' '.join(x for x in [content, snippet] if x)
    sents=split_sent(source_text)
    cat=classify((title+' '+source_text).lower())
    bullets=[]
    if sents:
        # Use actual article body when available, not just RSS teaser.
        bullets.extend(sents[:3])
    elif snippet:
        bullets.append(snippet)
    # second line: infer impact/focus from title/category
    low=(title+' '+source_text).lower()
    if cat=='stock':
        if any(w in low for w in ['trần','tăng mạnh','bứt phá','vượt đỉnh']):
            bullets.append('Điểm cần chú ý: cổ phiếu/nhóm ngành đang có biến động giá mạnh, cần kiểm tra thanh khoản và nguyên nhân hỗ trợ trước khi hành động.')
        elif any(w in low for w in ['rung lắc','giảm','bán','áp lực']):
            bullets.append('Tác động thị trường: tâm lý có thể thận trọng hơn; ưu tiên quản trị rủi ro và chờ vùng hỗ trợ/xác nhận.')
        else:
            bullets.append('Liên quan thị trường chứng khoán; nên đối chiếu với diễn biến giá, thanh khoản và nhóm ngành hưởng lợi.')
    elif cat=='business':
        bullets.append('Tác động doanh nghiệp: cần xem ảnh hưởng tới doanh thu, lợi nhuận, dòng tiền hoặc nghĩa vụ tài chính trong các kỳ tới.')
    elif cat=='macro':
        bullets.append('Tác động vĩ mô/ngành: có thể ảnh hưởng chi phí vốn, dòng tiền hoặc kỳ vọng thị trường; cần theo dõi phản ứng nhóm liên quan.')
    else:
        bullets.append('Cần theo dõi thêm dữ liệu xác nhận và phản ứng của thị trường trong các phiên tới.')
    # third line: action lens
    bullets.append('Góc nhìn đầu tư: chưa xem là tín hiệu mua/bán độc lập; dùng như thông tin nền để kết hợp PTKT, định giá và quản trị vị thế.')
    # de-dup and length cap
    uniq=[]
    for b in bullets:
        b=clean(b)
        if b and b not in uniq: uniq.append(b[:260])
    return '\n'.join('• '+b for b in uniq[:5])

def process_obj(obj):
    arr=obj if isinstance(obj,list) else obj.get('items') if isinstance(obj,dict) else []
    changed=0
    if isinstance(arr,list):
        for item in arr:
            if not isinstance(item,dict): continue
            original = clean(item.get('snippet') or item.get('description') or item.get('summary') or '')
            ai=make_summary(item)
            item['ai_summary']=ai
            item['summary_full']=ai
            # Web should show the richer article-based summary when available.
            item['summary']=ai or original
            if original:
                item['snippet']=original
                item['description']=original
            changed+=1
    if isinstance(obj,dict):
        obj['aiSummaryUpdatedAt']=datetime.now(TZ).isoformat(timespec='seconds')
    return changed

def main():
    total=0
    for p in FILES+EN_FILES:
        if not p.exists():
            print('missing',p); continue
        obj=json.loads(p.read_text(encoding='utf-8'))
        n=process_obj(obj); total+=n
        p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
        print(p,n)
    print(json.dumps({'updated':total,'at':datetime.now(TZ).isoformat(timespec='seconds')},ensure_ascii=False))
if __name__=='__main__': main()
