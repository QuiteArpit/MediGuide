# MediGuide frontend

This is a dependency-free HTML/CSS/JavaScript single-page interface for the
MediGuide FastAPI backend.

## Run locally

Start the backend from the repository root:

```bash
.venv/bin/uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000
```

In another terminal, serve this directory (opening `index.html` directly may
be blocked by browser CORS/file-origin rules):

```bash
cd src/app
python -m http.server 5500
```

Open <http://127.0.0.1:5500>. The frontend uses
`http://127.0.0.1:8000` by default. To use another backend URL, append it as
an encoded `api` query parameter:

```text
http://127.0.0.1:5500/?api=http%3A%2F%2F127.0.0.1%3A9000
```

The interface fetches `/questions`, submits `/screening`, queries
`/food-query`, and generates `/diet-plan`. It displays backend errors and
offline states without hiding them. Emergency screening results are displayed
with a prominent red warning and emergency-service guidance.

All screening and diet content is educational and does not replace advice
from a healthcare professional.
