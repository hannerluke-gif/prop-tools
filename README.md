# Prop Tools (Flask + Bootstrap Starter)

A minimal Flask project scaffolded with Bootstrap 5, ready for rapid prototyping or extension into a larger application. The project files live in the `propfirm_bootstrap/` folder.

## Features
- Flask app with a single route (`/`)
- Jinja2 template inheritance (`base.html` + `index.html`)
- Bootstrap 5.3.3 via CDN
- Organized static asset structure (`static/css/style.css`)
- Virtual environment isolation (`.venv/`)
- VS Code tasks to quickly run the development server

## Project Structure
```
propfirm_bootstrap/
  app.py
  templates/
    base.html
    index.html
  static/
    css/
      style.css
  .vscode/
    tasks.json
  .gitignore
  README.md
```

## Requirements
- Python 3.10+ (earlier versions 3.8+ likely work, but not tested here)
- PowerShell (for provided commands) / VS Code

## 1. Create & Activate Virtual Environment
From the project root:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
If activation is blocked by policy:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

## 2. Install Dependencies
```powershell
pip install Flask
pip freeze > requirements.txt   # optional lock
```

## 3. Run the App (Direct Python)
```powershell
.\.venv\Scripts\Activate.ps1
python app.py
```
Visit: http://127.0.0.1:5000/

## 4. Run the App (Flask CLI)
```powershell
.\.venv\Scripts\Activate.ps1
$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "development"   # enables auto reload & debugger
flask run
```

## 5. VS Code Task Usage
Press: `Ctrl+Shift+P` → `Run Task...` → choose:
- `Flask: Run app.py (python)` OR
- `Flask: flask run (env vars)`

The second task keeps a background server using the Flask CLI.

## 6. Modifying Templates
- Add new pages: create `templates/yourpage.html` extending `base.html`.
- Add a route in `app.py`:
```python
@app.route('/about')
def about():
    return render_template('about.html')
```

## 7. Adding More Dependencies
Add to environment:
```powershell
pip install <package>
pip freeze > requirements.txt
```

## 8. Environment Variables (Optional Pattern)
Instead of hardcoding config, you can later use:
```python
import os
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-insecure')
```
Set in PowerShell before running:
```powershell
$env:SECRET_KEY = "some-secret"
```

## 9. Production Considerations
- Use a production WSGI server (e.g. `waitress`, `gunicorn` on Linux) instead of `app.run()`.
- Set `FLASK_ENV` (or `FLASK_DEBUG`) appropriately and avoid leaving debug mode enabled in production.
- Consider `.env` management via `python-dotenv`.

## 10. Suggested Next Enhancements
- Add `README` badges & license
- Implement Blueprints for modularization
- Add a `config.py` with multiple environments (Dev/Staging/Prod)
- Integrate a database (SQLite + SQLAlchemy)
- Add form handling with WTForms or Flask-WTF
- Add basic tests (`pytest` + `coverage`)

## 11. Simple Test That App Imports
Create `tests/test_basic.py` (future enhancement idea):
```python
def test_import():
    import app
    assert app.app is not None
```
Run (after installing pytest):
```powershell
pytest -q
```

## 12. Cleaning Up
To deactivate the virtual environment:
```powershell
deactivate
```

## 13. Git Ignore Notes
The `.gitignore` already excludes `.venv/` and Python bytecode. If you add `requirements.txt`, commit it.

## 14. License
Choose a license (e.g., MIT) and add a `LICENSE` file if this becomes public.

## Hero slide animation change

The hero carousel was updated to use a "slide in from the right" animation for incoming slides. Changes made:

- `static/scss/components/_hero.scss`: slides are now absolutely positioned and animated using `transform: translateX(...)` so entering slides slide in from the right. The CSS transition duration is ~520ms.
- `static/js/components/hero.js`: JS now coordinates `.is-active` and `.is-exiting` classes so outgoing slides animate out and incoming slides animate in. Rapid navigation is locked during the transition to avoid visual glitches.

How to preview

1. Make sure your dev tasks are running (Sass watch + Flask dev). Sass should auto-compile; the repo's watcher prints a successful compile message when ready.
2. Open the app in your browser (e.g. `http://127.0.0.1:5000/`).
3. Wait for the carousel to auto-rotate or click the next/prev arrows to observe the slide-in-from-right animation. If you want the outgoing slide to animate more aggressively, we can tweak the `.is-exiting` styles or timing.

If you want, I can add an accessibility improvement to pause rotation while the hero has keyboard focus, or tune easing/duration for a snappier feel.

---
Happy building! Feel free to request a `launch.json`, Blueprint refactor, or database integration next.
