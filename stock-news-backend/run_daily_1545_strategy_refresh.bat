@echo off
cd /d C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend
C:\Users\HoaD-CVDT\AppData\Local\Python\pythoncore-3.14-64\python.exe -X utf8 run_daily_1545_strategy_refresh.py >> logs\daily_1545_strategy_refresh_stdout.log 2>&1
