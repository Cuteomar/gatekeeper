#!/usr/bin/env python3
"""Entry point for the GateKeeper Flask application.

Usage
-----
    flask run            # Development server
    gunicorn run:app     # Production (Render, Railway, etc.)
    python run.py        # Direct execution
"""

import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV", "production") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)