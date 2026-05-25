#!/usr/bin/env python3
"""Entry point for the RBAC Flask application.

Usage
-----
    flask run             # Uses FLASK_APP=run.py from .env
    python run.py         # Starts the development server directly
"""

import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)