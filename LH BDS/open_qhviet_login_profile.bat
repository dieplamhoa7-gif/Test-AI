@echo off
set CHROME=C:\Program Files\Google\Chrome\Application\chrome.exe
set PROFILE=C:\Users\HoaD-CVDT\.openclaw\workspace\.bds-browser-profile
if not exist "%CHROME%" (
  echo Chrome not found: %CHROME%
  pause
  exit /b 1
)
echo Opening QH Viet with the persistent BDS automation profile:
echo %PROFILE%
echo.
echo IMPORTANT: Do not delete this folder, otherwise QH Viet login cookies will be lost.
start "QH Viet BDS Profile" "%CHROME%" --remote-debugging-port=18800 --user-data-dir="%PROFILE%" --no-first-run --disable-popup-blocking https://qhviet.com/quy-hoach/thanh-pho-ho-chi-minh-hanh-chinh-2-cap
