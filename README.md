# UCS654 Lecture Repository

This repo holds my UCS654 assignments. Each assignment lives in its own folder named by the assignment number and topic.

## Folder layout

- `Assignment-1-Topsis/` — TOPSIS implementation with CLI, PyPI package scaffold, and a Flask web UI.
- Future assignments will be added as additional folders at this same level.

## How to use

1. Clone the repo or open it in VS Code.
2. Open the assignment folder you want to run.
3. Follow that folder's README for setup and execution steps (e.g., dependency install, running scripts, or starting the web app).

## Notes

- Keep new assignments self-contained inside their own folders.
- Include a README in every assignment folder so instructors can run it easily.
- Use virtual environments per assignment to avoid dependency conflicts.

## Deploy the TOPSIS webapp (Hugging Face Spaces)

This monorepo includes a Flask webapp at `Assignment-1-Topsis/webapp`. A root-level `Dockerfile` is included to deploy that subfolder directly to a Hugging Face Docker Space without creating a separate repository.

Steps:

- Push this repository to GitHub (ensure the root `Dockerfile` and `.dockerignore` are committed).
- On Hugging Face → Spaces → Create new Space → Type: Docker → Connect to this GitHub repo → Create Space.
- The Space will build using the root `Dockerfile`, which copies `Assignment-1-Topsis/webapp` and runs `app.py`.

Notes:

- The app binds to `0.0.0.0` and reads the port from the `PORT` environment variable.
- If you don’t want to connect GitHub, you can upload the files from `Assignment-1-Topsis/webapp/` directly to a new Docker Space instead.
