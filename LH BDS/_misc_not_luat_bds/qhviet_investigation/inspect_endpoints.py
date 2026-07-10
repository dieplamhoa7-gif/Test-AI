from pathlib import Path
s=(Path(__file__).parent/'components.js_v_1783689124.js').read_text(encoding='utf-8')
for term in ['api_resource','check_parcel','parcel','plan_info','plan_detail','url_to_point','document','identify','layer','feature']:
 print('\nTERM',term)
 start=0
 for k in range(10):
  i=s.lower().find(term.lower(), start)
  if i<0: break
  print('@',i, s[max(0,i-300):i+700].replace('\n',' ')[:1200])
  start=i+len(term)
