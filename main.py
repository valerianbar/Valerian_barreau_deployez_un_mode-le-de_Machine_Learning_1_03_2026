# from src.model import predict
# from db_rh_connect import engine


# data = {
#     # ===== NUMÉRIQUES (toutes obligatoires) =====
#     "age": 23,
#     "revenu_mensuel": 2000,
#     "nombre_experiences_precedentes": 3,
#     "nombre_heures_travailless": 40,
#     "annee_experience_totale": 10,
#     "annees_dans_l_entreprise": 3,
#     "annees_dans_le_poste_actuel": 2,
#     "distance_domicile_travail": 10,
#     "nb_formations_suivies": 2,
#     "satisfaction_employee_environnement": 3,
#     "note_evaluation_precedente": 3,
#     "niveau_hierarchique_poste": 2,
#     "satisfaction_employee_nature_travail": 3,
#     "satisfaction_employee_equipe": 3,
#     "satisfaction_employee_equilibre_pro_perso": 3,
#     "note_evaluation_actuelle": 3,
#     "nombre_participation_pee": 1,
#     "nombre_employee_sous_responsabilite": 0,
#     "niveau_education": 3,
#     "annees_depuis_la_derniere_promotion": 1,
#     "annes_sous_responsable_actuel": 2,
#     "ratio_stagnation": 0.33,
#     "satisfaction_globale": 1.0,
#     "stress": 5,

#     # ===== CATÉGORIELLES =====
#     "genre": "M",
#     "poste": "Tech Lead",
#     "departement": "consulting",
#     "statut_marital": "Marié(e)",
#     "domaine_etude": "Infra & Cloud",
#     "frequence_deplacement": "Occasionnel",
#     "heure_supplementaires": "Oui",
#     "augementation_salaire_precedente": "15 %"
# }

# result = predict(employee_id)

# print("Prediction:", result["prediction"])
# print("Probability:", result["probability"])
from src.model import predict

def run(employee_id):
    result = predict(employee_id)
    print(f"Résultat pour {employee_id}: {result}")

if __name__ == "__main__":
    run(1)  # Remplacez par un ID d'employé valide de votre base de données
    run(999)
    run(123)
    run(456)
    run(789)
    run(10)
    run(11)
    run(12)
    run(13)
   


 