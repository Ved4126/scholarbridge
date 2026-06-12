# Setup Instructions

## Prerequisites
- **Python Version:** Python 3.9 or higher is recommended.
- **Git:** Ensure you have Git installed to clone the repository.

## Virtual Environment Setup
It is highly recommended to use a virtual environment (`.venv`) to isolate project dependencies.

1. Create the virtual environment in the project root:
   ```bash
   python3 -m venv .venv
   ```
2. Activate the virtual environment:
   - On macOS/Linux: `source .venv/bin/activate`
   - On Windows: `.venv\Scripts\activate`

## Dependency Installation
With the virtual environment active, install the required packages:
```bash
pip install fastapi uvicorn pydantic pytest
```
*(Optional: install `httpx` for TestClient support in newer FastAPI versions if required).*

## Running pytest
To run the full test suite (107 tests), ensure your virtual environment is activated and run:
```bash
PYTHONPATH=. pytest tests/ -v
```

## Running FastAPI Locally
To start the local development server:
```bash
PYTHONPATH=. uvicorn backend.app.main:app --reload
```
The server will be available at `http://127.0.0.1:8000`.

## Swagger / OpenAPI Docs
Once the server is running, navigate to:
`http://127.0.0.1:8000/docs`
This interactive UI allows you to test endpoints directly from the browser.

## Common Troubleshooting

### "Cannot find module pydantic" in VS Code / Cursor
If your editor shows red squiggly lines claiming a module is missing, it is using the global Python interpreter instead of the virtual environment.
**Fix:**
1. Open the Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`).
2. Type `Python: Select Interpreter` and hit Enter.
3. Choose the interpreter located at `./.venv/bin/python`.

### Resetting local repo safely from GitHub
If you need to discard local changes and force your repository to match `origin/main`:
```bash
git fetch origin
git reset --hard origin/main
git clean -fd
```
