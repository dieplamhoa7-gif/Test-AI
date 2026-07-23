import sys
import importlib.util
sys.path.insert(0, 'bds_engine')
from playwright_bds_scraper import Listing
spec = importlib.util.spec_from_file_location('valuation_api', 'bds_engine/web_valuation_api.fastmode_backup_20260626_2200.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
_filter_buckets_by_transaction = module._filter_buckets_by_transaction

sale = Listing('BDS', 'Bán nhà riêng', 4.2, 60, 70, 'https://batdongsan.com.vn/ban-nha-rieng-phuong-gia-dinh-pr1')
rental = Listing('BDS', 'Cho thuê căn hộ 12 triệu/tháng', 0.012, 60, 0.2, 'https://batdongsan.com.vn/cho-thue-can-ho-phuong-gia-dinh-pr2')
generic_sale = Listing('BDS', 'Nhà đất bán Phường Gia Định', None, None, None, 'https://batdongsan.com.vn/nha-dat-ban-phuong-gia-dinh-tp-ho-chi-minh')
buckets = {'Batdongsan.com.vn': [sale, rental, generic_sale]}

rent_urls = [x.url for xs in _filter_buckets_by_transaction(buckets, True).values() for x in xs]
buy_urls = [x.url for xs in _filter_buckets_by_transaction(buckets, False).values() for x in xs]
assert rent_urls == [rental.url], rent_urls
assert buy_urls == [sale.url, generic_sale.url], buy_urls
print('PASS: rent has only /cho-thue-; buy has no rental URL or monthly listing')
