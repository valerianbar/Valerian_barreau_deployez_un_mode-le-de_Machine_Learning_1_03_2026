from sqlmodel import SQLModel, Field
from typing import Optional

class Prediction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: int
    prediction: int
    probability: float