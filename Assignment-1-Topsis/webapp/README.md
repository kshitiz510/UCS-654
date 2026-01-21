# TOPSIS Webapp

A lightweight Flask UI for running TOPSIS on CSV datasets.

## Quick start

1. Create a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the server from this folder:
   ```bash
   python app.py
   ```
4. Open http://localhost:5000 and upload your CSV (first column identifier, rest criteria). Use the sample toggle if you want to try `test_data.csv` from the project root.

## Notes

- Enter one weight and impact per criterion column (excluding the identifier column).
- Impacts: `+` means higher is better, `-` means lower is better.
- The results table can be downloaded as CSV.

## Deploy (free) – Hugging Face Spaces (Docker)

This app is ready to deploy on Hugging Face Spaces using a Docker Space.

### Option A: Create a new repo with only the webapp

1. Create a new GitHub repo and copy the contents of this `webapp/` folder into the repo root (so `Dockerfile`, `app.py`, `requirements.txt` are at the top level).
2. Push to GitHub.
3. On https://huggingface.co/spaces, click “Create new Space” → “Docker” → connect your repo → Create Space.
4. The build will start; once it’s running, your Space will be publicly accessible.

### Option B: Upload files directly

1. Create a new Space (type: Docker).
2. Drag-and-drop the files from this `webapp/` folder (including `Dockerfile`, `app.py`, `requirements.txt`, `templates/`, `static/`).
3. Commit changes in the Space – it will build and launch automatically.

Notes:

- The app binds to `0.0.0.0` and reads the port from `$PORT` (set by Spaces).
- No extra config needed; the included `Dockerfile` installs deps and runs `python app.py`.
