import asyncio, time
from config import load_settings
from ai_client import NineRouterClient, make_role_client

async def probe(name, client):
    t=time.perf_counter()
    try:
        txt=await client.chat('Bạn là trợ lý kiểm tra độ trễ. Trả lời đúng 1 từ: OK.', 'Ping', temperature=0)
        dt=time.perf_counter()-t
        print(f'{name}: ok {dt:.2f}s model={client.model} base={client.base_url} reply={txt[:40]!r}')
    except Exception as e:
        dt=time.perf_counter()-t
        print(f'{name}: ERR {dt:.2f}s model={getattr(client,"model",None)} base={getattr(client,"base_url",None)} {type(e).__name__}: {str(e)[:200]}')

async def main():
    s=load_settings()
    main=NineRouterClient(s.nineouter_api_key,s.nineouter_base_url,s.nineouter_model,timeout=25)
    fast=make_role_client(main,s.fast_api_key,s.fast_base_url,s.fast_model,timeout=25)
    bds=make_role_client(main,s.bds_api_key,s.bds_base_url,s.bds_model,timeout=25)
    report=make_role_client(main,s.report_api_key,s.report_base_url,s.report_model,timeout=25)
    print('timeouts configured:', 'ai', s.ai_timeout, 'fast', s.ai_fast_timeout)
    for name,c in [('main',main),('fast',fast),('bds',bds),('report',report)]:
        await probe(name,c)

asyncio.run(main())
