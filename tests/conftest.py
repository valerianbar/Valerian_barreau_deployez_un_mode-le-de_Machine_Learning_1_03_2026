"""
Configuration partagée pour les tests pytest.

On évite que les tests dépendent d'une vraie DB Postgres ou du fichier model.pkl
en moquant la fonction `predict` utilisée par l'API.
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Ajoute la racine du projet au PYTHONPATH pour que `from src...` fonctionne
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# On stub `db_rh_connect` AVANT que src.model ne tente de l'importer.
# Sinon il essaie de se connecter à Postgres au moment de l'import.
sys.modules.setdefault("db_rh_connect", MagicMock(engine=MagicMock()))


@pytest.fixture
def client():
    """Client de test FastAPI."""
    from fastapi.testclient import TestClient
    from src.api.main import app
    return TestClient(app)
