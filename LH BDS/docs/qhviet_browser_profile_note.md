# QH Việt login profile note

QH Việt planning automation uses the persistent Chrome profile defined in `planning_browser_popups.js`:

```text
C:\Users\HoaD-CVDT\.openclaw\workspace\.bds-browser-profile
```

Do **not** delete this folder. It contains QH Việt login cookies/session that Hòa Đại ka already logged in.

Use this helper if login is needed again:

```text
C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\open_qhviet_login_profile.bat
```

The helper opens Chrome with:

```text
--remote-debugging-port=18800
--user-data-dir=C:\Users\HoaD-CVDT\.openclaw\workspace\.bds-browser-profile
```

Operational rule:
- For QH Việt, keep using this persistent automation profile.
- Do not switch QH Việt planning to per-job temporary Chrome profiles.
- Do not clear cookies/cache for this profile unless Hòa Đại ka explicitly asks.
