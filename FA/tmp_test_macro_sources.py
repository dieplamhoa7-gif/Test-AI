from macro.fetchers import yfinance_global, worldbank_macro, fiinprox_excel
import json
res={}
yf=yfinance_global.fetch_core(); res['yf_keys']=list(yf.get('data',{}).keys()); res['yf_errors']=yf.get('errors')
wb=worldbank_macro.fetch(years=8); res['wb_count']=len(wb.get('data',{})); res['wb_errors']=wb.get('errors')
fi=fiinprox_excel.fetch(); res['fiin_rows']=fi.get('rowCount'); res['fiin_indicators']=fi.get('indicatorCount')
print(json.dumps(res,ensure_ascii=False,indent=2))
