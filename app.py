"""Canonical Trash2Cash entrypoint.

Run with `python app.py` from the repository root. All routes and
business logic live in project.py; this file just starts the server.
"""

from project import app

if __name__ == "__main__":
    app.run(debug=True)
