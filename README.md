# Notre Dame Football — News & Feeds

- Static front-end served by Flask (`server.py`) for local preview or any simple host.
- Articles are refreshed by **GitHub Actions** every 30 minutes (see `.github/workflows/collect.yml`) which runs `collect.py` and writes `items.json` back to the repo.
- The UI reads from `items.json` — no backend dependency in production if you serve the files statically.

## Local preview
```bash
pip install -r requirements.txt
python server.py
# http://localhost:8080
```
