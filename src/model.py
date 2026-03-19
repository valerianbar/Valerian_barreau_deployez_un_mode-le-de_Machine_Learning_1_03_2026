import pandas as pd
import numpy as np
import joblib
import os

MODEL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../models/model.pkl")
)

def load_model():
    data = joblib.load(MODEL_PATH)
    if isinstance(data, dict):
        return data["model"], data.get("columns", []), data.get("threshold", 0.5)
    else:
        return data, [], 0.5

def predict(input_data: dict):
    model, columns, threshold = load_model()

    df = pd.DataFrame([input_data])
    df = pd.get_dummies(df, drop_first=True)

    if len(columns) > 0:
        df = df.reindex(columns=columns, fill_value=0)

    proba = model.predict_proba(df)[0][1]
    prediction = int(proba >= threshold)

    return {
        "prediction": prediction,
        "probability": float(proba)
    }
