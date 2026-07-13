"""
Set DATABASE_URL before ANY test file (or conftest fixture) gets a chance
to import backend.db — that module binds `engine = create_engine(DATABASE_URL)`
at import time, so the env var must be set before first import, not inside
a fixture (see the identical bug fixed in the AI Engineer submission's
CHROMA_PATH handling for the same root cause).

This runs at conftest.py's own import time, which pytest guarantees happens
before it collects and imports any test module.
"""
import os
import tempfile

_test_db_path = os.path.join(tempfile.mkdtemp(prefix="wallet_bill_test_"), "test.db")
os.environ["DATABASE_URL"] = f"sqlite:///{_test_db_path}"
