from src.model import predict
import pandas as pd
from db_rh_connect import engine

# charger tous les employés
df = pd.read_sql("SELECT * FROM employes", engine)

results = []

for emp_id in df["id_employee"]:
    res = predict(emp_id)

    if "prediction" in res:
        results.append(res["prediction"])

# convertir en DataFrame
df_results = pd.DataFrame(results, columns=["prediction"])

# stats
total = len(df_results)
quit_count = df_results["prediction"].sum()
stay_count = total - quit_count

print(f"Total employés: {total}")
print(f"Quittent: {quit_count}")
print(f"Restent: {stay_count}")
print(f"Taux de départ: {quit_count/total:.2%}")