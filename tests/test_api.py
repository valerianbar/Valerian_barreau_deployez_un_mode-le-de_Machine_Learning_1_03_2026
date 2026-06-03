"""
Tests des endpoints de l'API HR Attrition.
La fonction `predict` est moquée pour ne pas dépendre de la DB / du modèle.
"""
from unittest.mock import patch


# ───────────────────────────────────────────────
# Endpoint racine
# ───────────────────────────────────────────────
def test_home_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_home_returns_expected_message(client):
    response = client.get("/")
    assert response.json() == {"message": "API is running"}


# ───────────────────────────────────────────────
# Endpoint /predict/{employee_id}
# ───────────────────────────────────────────────
def test_predict_returns_valid_response(client):
    """Quand `predict` renvoie un résultat valide, l'API renvoie 200 et le bon schéma."""
    with patch("src.api.main.predict") as mock_predict:
        mock_predict.return_value = {"prediction": 1, "probability": 0.87}
        response = client.get("/predict/42")

    assert response.status_code == 200
    body = response.json()
    assert body == {"prediction": 1, "probability": 0.87}


def test_predict_returns_404_when_employee_not_found(client):
    """Quand `predict` renvoie une erreur, l'API renvoie 404."""
    with patch("src.api.main.predict") as mock_predict:
        mock_predict.return_value = {"error": "Employé introuvable"}
        response = client.get("/predict/9999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Employé introuvable"


def test_predict_passes_employee_id_to_model(client):
    """Vérifie que l'ID de l'employé est bien passé à `predict`."""
    with patch("src.api.main.predict") as mock_predict:
        mock_predict.return_value = {"prediction": 0, "probability": 0.12}
        client.get("/predict/123")
        mock_predict.assert_called_once_with(123)


def test_predict_rejects_non_integer_id(client):
    """FastAPI doit rejeter un ID non numérique avec 422."""
    response = client.get("/predict/not-a-number")
    assert response.status_code == 422


# ───────────────────────────────────────────────
# Validation du schéma PredictionResponse
# ───────────────────────────────────────────────
def test_prediction_response_schema():
    from src.api.schemas import PredictionResponse

    obj = PredictionResponse(prediction=1, probability=0.5)
    assert obj.prediction == 1
    assert obj.probability == 0.5
