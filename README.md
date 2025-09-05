# Notre Dame Football — Sports News Bot

Purdue-style Flask app that fetches and filters Notre Dame **football** news and renders a clean, mobile-first feed.

## Run locally

```bash
pip install -r requirements.txt
python3 collect.py      # fetch feeds → items.json
python3 server.py       # open http://127.0.0.1:5000
