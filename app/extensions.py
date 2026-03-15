"""Shared Flask extensions.

Keeping extension objects here avoids circular imports (e.g. models importing main).
"""

from flask_sqlalchemy import SQLAlchemy

# Create the extension without binding to an app yet.
db = SQLAlchemy()
