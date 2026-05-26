$ErrorActionPreference = 'Stop'
Set-Location 'C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend'
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
python run_after_close_output_lh.py
