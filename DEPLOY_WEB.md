# J.A.R.V.I.S. Web Deployment

This web version is a browser chat layer for the desktop app. It works on phones, tablets, and computers through one URL.

## Deploy on Render

1. Put this folder in a GitHub repository and push the files.
2. Open [render.com](https://render.com), choose **New > Blueprint**, and select the repository.
3. Render will read `render.yaml` and create the `jarvis-web` service.
4. In the service environment settings, add `OPENAI_API_KEY` with your provider key.
5. Deploy. Open the generated `https://...onrender.com` URL on your phone.

The API key stays on the server and is never sent to the browser.

## Local test

```powershell
python -m pip install -r requirements-web.txt
$env:OPENAI_API_KEY = "your-key"
python -m uvicorn web_app:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000` in a browser. For phone testing on the same Wi-Fi, run with `--host 0.0.0.0` and open the computer's local IP plus port `8000`.

## Important limitation

The browser version does not expose Windows-only actions, microphone wake listening, local file access, or local Ollama. Those remain in `jarvis1.py`. To use Ollama in the cloud, it must be hosted behind a secure reachable API; do not expose a home Ollama port directly to the internet.
