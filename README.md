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
le tout conteneurisé avec Docker, testé en CI/CD GitHub Actions
et **déployé en production sur Hugging Face Spaces avec une base PostgreSQL hébergée sur Neon**.

---

## 🌐 Démo live

| Lien | URL |
|---|---|
| 🚀 **API en prod (HF Spaces)** | https://valerian2121-hr-attrition-api.hf.space/ |
| 📚 **Documentation Swagger** | https://valerian2121-hr-attrition-api.hf.space/docs |
| 🎯 **Exemple de prédiction** | https://valerian2121-hr-attrition-api.hf.space/predict/1 |

---

## Sommaire

- [Stack technique](#stack-technique)
- [Architecture](#architecture)
- [Structure du projet](#structure-du-projet)
- [Démarrage rapide](#démarrage-rapide)
- [Utilisation de l'API](#utilisation-de-lapi)
- [Tests](#tests)
- [CI/CD](#cicd)
- [Déploiement en production](#déploiement-en-production)
- [Commandes utiles](#commandes-utiles)

---

## Stack technique

| Domaine | Outil |
|---|---|
| Langage | Python 3.13 |
| API | FastAPI + Uvicorn |
| ML | scikit-learn, LightGBM, XGBoost, SHAP |
| Base de données (dev) | PostgreSQL 16 via Docker Compose |
| Base de données (prod) | **Neon** — Postgres managé serverless |
| ORM | SQLAlchemy |
| Conteneurisation | Docker + Docker Compose |
| Stockage modèle | Git LFS (puis Xet sur HF) |
| Tests | pytest + pytest-cov |
| Lint | ruff |
| CI/CD | GitHub Actions |
| Registry image | GHCR (GitHub Container Registry) |
| Hébergement prod | **Hugging Face Spaces** (SDK Docker) |

---

## Architecture

### En développement local
```
┌─────────────────┐       ┌──────────────────┐
│   Client HTTP   │──────▶│  FastAPI (:8000) │
└─────────────────┘       │  src/api/main    │
                          └────────┬─────────┘
                                   │ predict(id)
                          ┌────────▼─────────┐
                          │   src/model.py   │
                          │  (model.pkl)     │
                          └────────┬─────────┘
                                   │ SQLAlchemy
                          ┌────────▼─────────┐
                          │  Postgres 16     │
                          │  Docker (:5433)  │
                          └──────────────────┘
```
Orchestré par `docker-compose.yml` sur un réseau Docker interne avec healthcheck `pg_isready`.

### En production
```
┌─────────────────┐       ┌────────────────────────┐       ┌─────────────────────┐
│   Client HTTP   │──────▶│  HF Space (Docker)     │──────▶│  Neon Postgres      │
│   (browser)     │       │  FastAPI (:7860)       │  SSL  │  eu-central-1.aws   │
└─────────────────┘       │  src/api/main          │       │  (serverless)       │
                          └────────────────────────┘       └─────────────────────┘
                                   ▲
                                   │ DATABASE_URL (HF secret)
```
L'API tourne sur **Hugging Face Spaces** (image Docker, user non-root uid 1000, port 7860)
et se connecte à **Neon** via SSL grâce au secret `DATABASE_URL` injecté à l'exécution.

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

## Déploiement en production

### Architecture cible

L'application est déployée **gratuitement et sans carte bancaire** sur deux services :

1. **Hugging Face Spaces** (SDK Docker) — héberge l'API
2. **Neon** — fournit la base PostgreSQL managée

### 1. Base de données : Neon

[Neon](https://neon.tech) est un Postgres serverless qui propose un tier gratuit
généreux (3 Go, projets illimités, pas de carte). Le projet utilise une instance
hébergée en `eu-central-1` (Frankfurt).

**Setup initial** :

```bash
# 1. Créer un compte sur https://neon.tech et un projet "mlops-rh"
# 2. Récupérer la connection string (Dashboard → Connection string)
# 3. Importer les CSV dans Neon depuis le conteneur local
export DATABASE_URL="postgresql://<user>:<pwd>@<host>.neon.tech/neondb?sslmode=require"
docker compose run --rm \
  -e DATABASE_URL="$DATABASE_URL" \
  api python import_data.py
# → ✅ Tables importées
```

Vérification du contenu :
```sql
SELECT COUNT(*) FROM employees;   -- 1470
SELECT COUNT(*) FROM evaluations; -- 1470
SELECT COUNT(*) FROM sondage;     -- 1470
```

### 2. API : Hugging Face Spaces

Le projet est configuré comme un **Space Docker** : HF lit le Dockerfile à la racine,
le build et lance le conteneur. Les métadonnées du Space sont déclarées dans
l'en-tête YAML de ce README :

```yaml
---
title: HR Attrition API
emoji: 🧑‍💼
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---
```

**Particularités du Dockerfile pour HF** :
- Utilisateur non-root `user` (uid 1000) — obligatoire sur HF Spaces
- Port **7860** au lieu de 8000 — port standard des Spaces
- Le modèle `models/model.pkl` est tracké via **Git LFS** (HF stocke via Xet)

**Setup initial** :

```bash
# 1. Créer un Space sur https://huggingface.co/new-space
#    SDK: Docker → Blank, Hardware: CPU basic (gratuit), Public

# 2. Settings → Variables and secrets → New secret
#    Name:  DATABASE_URL
#    Value: postgresql://<user>:<pwd>@<host>.neon.tech/neondb?sslmode=require

# 3. Créer un token Write sur https://huggingface.co/settings/tokens

# 4. Ajouter HF comme remote git et pousser
git remote add hf https://huggingface.co/spaces/<username>/hr-attrition-api
git push hf main
# Username: <username>
# Password: hf_xxxxxxxxxxxx (le token Write, PAS le mot de passe HF)
```

### 3. Workflow de déploiement

```
                    git push origin main
GitHub ──────────────────────────────────┐
  │                                      │
  │ déclenche                            ▼
  │                            ┌────────────────────┐
  ▼                            │  GitHub Actions    │
GHCR (image taggée latest)     │  Lint + Tests +    │
                               │  Build + Push GHCR │
                               └────────────────────┘

                    git push hf main
Hugging Face ─────────────────────────────┐
  │                                       │
  │ rebuild auto                          ▼
  ▼                            ┌─────────────────────┐
hf.space (API en prod)         │  HF Space (Docker)  │
                               │  → injection secret │
                               │  → start uvicorn    │
                               └─────────────────────┘
```

À chaque push sur `hf main`, HF rebuild l'image Docker en 5–10 min et redémarre
le service. La variable d'env `DATABASE_URL` est injectée automatiquement depuis
les secrets HF.

### 4. Sécurité

- ✅ Aucun secret hardcodé dans le code (tout via `os.getenv("DATABASE_URL")`)
- ✅ Connexion Postgres chiffrée (`?sslmode=require`)
- ✅ Le token HF est **Write-only** et révocable
- ✅ Conteneur lancé en **non-root** (uid 1000) sur HF
- ✅ Le modèle `model.pkl` est versionné via Git LFS (pas dans l'image source)

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

| Variable | Défaut / Source | Description |
|---|---|---|
| `DATABASE_URL` (dev) | `postgresql://postgres:password@db:5432/rh_db_connect` | URL Postgres locale (résolution `db` dans le réseau Docker Compose) |
| `DATABASE_URL` (prod) | **HF Space secret** | URL Neon : `postgresql://...@*.neon.tech/neondb?sslmode=require` |
| `COMPOSE_PROJECT_NAME` | `mlops_rh` | Nom de projet Compose stable (évite les bugs d'encodage liés au `è` du dossier) |

---

## Auteur

**Valérian Barreau** – Formation OpenClassrooms *AI Engineer*
Projet 7 : *Déployez un modèle de Machine Learning*
