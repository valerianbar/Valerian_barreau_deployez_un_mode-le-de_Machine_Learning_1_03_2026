from fastapi import FastAPI, HTTPException
from src.model import predict
from src.api.schemas import PredictionResponse

app = FastAPI(title="HR Attrition API")

@app.get("/")
def home():
    return {"message": "API is running"}

@app.get("/predict/{employee_id}", response_model=PredictionResponse)
def get_prediction(employee_id: int):
    result = predict(employee_id)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result