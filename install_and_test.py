import subprocess
import sys
from pathlib import Path

packages = [
    "requests",
    "beautifulsoup4",
    "feedparser",
    "python-dotenv",
]

for pkg in packages:
    result = subprocess.run([sys.executable, "-m", "pip", "install", pkg])
    if result.returncode != 0:
        sys.exit(result.returncode)

test_file = Path("test_import.py")
test_file.write_text(
    "import requests\n"
    "from bs4 import BeautifulSoup\n"
    "import feedparser\n"
    "from dotenv import load_dotenv\n"
    "print('OK')\n",
    encoding="utf-8",
)

result = subprocess.run([sys.executable, str(test_file)], capture_output=True, text=True)
if result.returncode != 0:
    for pkg in packages:
        retry = subprocess.run([sys.executable, "-m", "pip", "install", pkg])
        if retry.returncode != 0:
            sys.exit(retry.returncode)
    result = subprocess.run([sys.executable, str(test_file)], capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(result.returncode)

sys.exit(0)
