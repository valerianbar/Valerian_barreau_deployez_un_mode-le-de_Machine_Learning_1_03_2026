import pandas as pd
import joblib
import os
from sqlalchemy import text
from db_rh_connect import engine

# ── PATH MODEL ─────────────────────────────────────
MODEL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../models/model.pkl")
)

# ── LOAD MODEL ─────────────────────────────────────
def load_model():
    data = joblib.load(MODEL_PATH)

    if isinstance(data, dict):
        return data["model"], data.get("columns", []), data.get("threshold", 0.5)
    else:
        return data, [], 0.5

# ── LOAD DATA FROM DB ──────────────────────────────
def load_employee(employee_id):
    query = text("SELECT * FROM employes WHERE id_employee = :id")
    return pd.read_sql(query, engine, params={"id": employee_id})

def predict(employee_id: int):
    model, columns, threshold = load_model()

    threshold = 0.5  # 👈 important

    df = load_employee(employee_id)

    if df.empty:
        return {"error": "Employé introuvable"}

    df = df.drop(columns=["id_employee"], errors="ignore")
    df = pd.get_dummies(df, drop_first=True)

    if len(columns) > 0:
        df = df.reindex(columns=columns, fill_value=0)

    # ✅ FIX ICI
    proba = model.predict_proba(df)[0]

    classes = model.classes_
    idx_quit = list(classes).index(1)
    prob_quit = proba[idx_quit]

    prediction = int(prob_quit >= threshold)

    return {
        "prediction": prediction,        # 1 = quitte
        "probability": float(prob_quit)
    }
   
# ── RUN ────────────────────────────────────────────
def run(employee_id):
    result = predict(employee_id)
    print(f"Résultat pour {employee_id}: {result}")
    return result
