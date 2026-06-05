---
title: HR Attrition API
emoji: 🧑‍💼
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# HR Attrition – API de prédiction de départs employés

Projet MLOps complet : entraînement d'un modèle de classification pour prédire
si un employé va quitter l'entreprise, puis exposition via une API REST,
le tout conteneurisé avec Docker et déployé via une pipeline CI/CD GitHub Actions.

---

## Sommaire

- [Stack technique](#stack-technique)
- [Architecture](#architecture)
- [Structure du projet](#structure-du-projet)
- [Démarrage rapide](#démarrage-rapide)
- [Utilisation de l'API](#utilisation-de-lapi)
- [Tests](#tests)
- [CI/CD](#cicd)
- [Commandes utiles](#commandes-utiles)

---

## Stack technique

| Domaine | Outil |
|---|---|
| Langage | Python 3.13 |
| API | FastAPI + Uvicorn |
| ML | scikit-learn, LightGBM, XGBoost, SHAP |
| Base de données | PostgreSQL 16 |
| ORM | SQLAlchemy |
| Conteneurisation | Docker + Docker Compose |
| Tests | pytest + pytest-cov |
| Lint | ruff |
| CI/CD | GitHub Actions |
| Registry | GHCR (GitHub Container Registry) |

---

## Architecture

```
┌─────────────────┐       ┌─────────────────┐
│   Client HTTP   │──────▶│  FastAPI (8000) │
└─────────────────┘       │  src/api/main   │
                          └────────┬────────┘
                                   │ predict(id)
                          ┌────────▼────────┐
                          │   src/model.py  │
                          │  (model.pkl)    │
                          └────────┬────────┘
                                   │ SQLAlchemy
                          ┌────────▼────────┐
                          │  PostgreSQL 16  │
                          │  (port 5433)    │
                          └─────────────────┘
```

Les deux services (`api` et `db`) sont orchestrés par `docker-compose.yml` sur
un réseau Docker interne. L'API attend que Postgres soit `healthy` avant de
démarrer (healthcheck `pg_isready`).

---

## Structure du projet

```
.
├── src/
│   ├── api/
│   │   ├── main.py            # Routes FastAPI
│   │   ├── schemas.py         # Modèles Pydantic
│   │   └── database.py        # Modèles SQLModel
│   └── model.py               # Chargement modèle + prédiction
├── tests/
│   ├── conftest.py            # Fixtures pytest
│   └── test_api.py            # Tests des endpoints
├── data/                      # CSV sources (sirh, eval, sondage)
├── models/
│   └── model.pkl              # Modèle entraîné (sklearn)
├── notebooks/                 # Notebooks d'exploration et d'entraînement
├── .github/workflows/
│   └── ci.yml                 # Pipeline CI/CD
├── db_rh_connect.py           # Connexion DB partagée
├── import_data.py             # Chargement des CSV dans Postgres
├── Dockerfile                 # Image de l'API
├── docker-compose.yml         # Orchestration api + db
├── requirements.txt           # Deps runtime
├── requirements-dev.txt       # Deps dev (pytest, ruff)
├── pytest.ini
└── .env                       # COMPOSE_PROJECT_NAME=mlops_rh
```

---

## Démarrage rapide

### Prérequis
- Docker Desktop installé et lancé
- Git

### 1. Cloner le repo
```bash
git clone https://github.com/valerianbar/Valerian_barreau_deployez_un_mode-le-de_Machine_Learning_1_03_2026.git
cd Valerian_barreau_deployez_un_mode-le-de_Machine_Learning_1_03_2026
```

### 2. Lancer le stack
```bash
docker compose up -d --build
```

Ce qui démarre :
- `postgres_rh` : Postgres 16 sur le port **5433** (évite le conflit avec un Postgres local sur 5432)
- `mlops_rh-api-1` : l'API FastAPI sur le port **8000**

### 3. Charger les données dans Postgres
La DB est vide au premier lancement. On importe les CSV depuis le conteneur :
```bash
docker compose exec api python import_data.py
```
→ `✅ Tables importées`

### 4. Tester
```bash
curl http://localhost:8000/
# {"message":"API is running"}

curl http://localhost:8000/predict/1
# {"prediction":0,"probability":0.46}
```

Ou ouvre la doc Swagger interactive : http://localhost:8000/docs

---

## Utilisation de l'API

### `GET /`
Health check.
```json
{ "message": "API is running" }
```

### `GET /predict/{employee_id}`
Prédit si l'employé `employee_id` risque de quitter l'entreprise.

**Réponse 200** :
```json
{
  "prediction": 1,
  "probability": 0.87
}
```
- `prediction` : `1` = risque de départ, `0` = reste
- `probability` : probabilité du départ ∈ [0, 1]

**Réponse 404** : employé introuvable dans la base.
```json
{ "detail": "Employé introuvable" }
```

---

## Tests

```bash
# Dans le conteneur (recommandé)
docker compose exec api python -m pytest tests/ -v

# Avec couverture
docker compose exec api python -m pytest --cov=src --cov-report=term-missing
```

Les tests utilisent `unittest.mock.patch` pour mocker la fonction `predict`
afin de tester l'API indépendamment du modèle et de la DB.

**7 tests couvrent** :
- Endpoint racine (`GET /`)
- Prédiction nominale (`GET /predict/{id}` → 200)
- Employé introuvable (`GET /predict/{id}` → 404)
- Transmission correcte de l'ID au modèle
- Validation des paramètres FastAPI (ID non numérique → 422)
- Schéma Pydantic `PredictionResponse`

---

## CI/CD

Pipeline déclenchée sur **push** et **pull request** vers `main` ([.github/workflows/ci.yml](.github/workflows/ci.yml)).

| Étape | Description |
|---|---|
| **lint** | `ruff check` sur tout le code |
| **test** | `pytest` avec couverture |
| **build-and-test** | Build de l'image Docker + smoke test (`docker compose up` + curl) |
| **push** | Push de l'image sur GHCR — **seulement sur `main`** |

Une fois mergée sur `main`, l'image est publiée à :
```
ghcr.io/valerianbar/valerian_barreau_deployez_un_mode-le-de_machine_learning_1_03_2026:latest
```

L'authentification utilise le `GITHUB_TOKEN` automatique : aucun secret à configurer.

---

## Commandes utiles

### Docker Compose
```bash
docker compose up -d              # Démarrer
docker compose up -d --build      # Rebuild + démarrer (après modif Dockerfile/requirements)
docker compose down               # Arrêter et supprimer les conteneurs
docker compose down -v            # ⚠️ supprime AUSSI les données Postgres
docker compose logs -f api        # Logs de l'API en direct
docker compose ps                 # État des services
```

### Connexion directe à Postgres
```bash
docker compose exec db psql -U postgres -d rh_db_connect
# \dt   pour lister les tables
# SELECT COUNT(*) FROM employees;
```

### Hors Docker (avec venv)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn src.api.main:app --reload
pytest
```

---

## Variables d'environnement

| Variable | Défaut | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql://postgres:password@db:5432/rh_db_connect` | URL Postgres (résolution `db` dans le réseau Docker) |
| `COMPOSE_PROJECT_NAME` | `mlops_rh` | Nom de projet Compose stable (évite les bugs d'encodage liés au `è` du dossier) |

---

## Auteur

**Valérian Barreau** – Formation OpenClassrooms *AI Engineer*
Projet 7 : *Déployez un modèle de Machine Learning*
