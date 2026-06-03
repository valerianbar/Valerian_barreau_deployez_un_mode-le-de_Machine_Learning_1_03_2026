import os
import pandas as pd
from sqlalchemy import create_engine

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5433/rh_db_connect"
)

engine = create_engine(DATABASE_URL)

employees = pd.read_csv("data/extrait_sirh.csv")
evaluations = pd.read_csv("data/extrait_eval.csv")
sondage = pd.read_csv("data/extrait_sondage.csv")

employees.to_sql(
    "employees",
    engine,
    if_exists="replace",
    index=False
)

evaluations.to_sql(
    "evaluations",
    engine,
    if_exists="replace",
    index=False
)

sondage.to_sql(
    "sondage",
    engine,
    if_exists="replace",
    index=False
)

print("✅ Tables importées")

