# Notre Dame Football — News & Feeds

Static site on GitHub Pages. Articles are refreshed by GitHub Actions (`.github/workflows/collect.yml`)
which runs `collect.py` and commits `items.json` back to the repo.

## Local preview
```
pip install -r requirements.txt
python collect.py   # generate items.json
python server.py    # open http://127.0.0.1:5000
```

## Deploy (GitHub Pages)
- Settings → Pages → Deploy from branch → main / (root)
- Optional: add `CNAME` for a custom domain, then set DNS
