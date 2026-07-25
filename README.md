# Health Future Engine

**"See your health before it happens."**

A predictive health platform: users build a digital health profile, get an
explainable disease-risk prediction from a Random Forest model, see a
year-by-year simulation of their health trajectory, and receive a
prioritized preventive action plan — all on one visual "horizon line" that
runs from recorded history through today into the future.

## Tech stack

| Module | Technology |
|---|---|
| Frontend | HTML, CSS, Bootstrap 5, vanilla JS, Chart.js |
| Backend | Python (Flask) |
| Database | MongoDB |
| Authentication | JWT (flask-jwt-extended) |
| Machine Learning | Scikit-learn (Random Forest) |
| Data Processing | Pandas, NumPy |

## Project structure

```
health-future-engine/
├── backend/
│   ├── app.py                  # Flask app factory + page & health routes
│   ├── config.py                # Env-driven configuration
│   ├── extensions.py            # MongoDB client, collections, JWT manager
│   ├── requirements.txt
│   ├── .env.example
│   ├── models/
│   │   ├── user_model.py        # users collection helpers
│   │   └── health_model.py      # profiles/predictions/recs/appts/history helpers
│   ├── routes/
│   │   ├── auth_routes.py       # /api/auth/*
│   │   ├── profile_routes.py    # /api/profile
│   │   ├── prediction_routes.py # /api/predict/*
│   │   ├── recommendation_routes.py
│   │   ├── appointment_routes.py
│   │   └── history_routes.py
│   ├── ml/
│   │   ├── train_model.py       # synthetic dataset + Random Forest trainer
│   │   └── predict.py           # risk prediction, explainability, simulation, recs
│   └── utils/
│       └── security.py          # bcrypt password hashing
└── frontend/
    ├── templates/                # Jinja2 pages (index, login, register, dashboard, profile, timeline)
    └── static/
        ├── css/style.css         # design system ("Horizon Line" motif)
        └── js/main.js            # auth/session + fetch helper shared by all pages
```

## Database collections (MongoDB)

- `users` — account + hashed password
- `health_profiles` — one document per user, latest vitals/lifestyle
- `health_predictions` — every risk prediction run, with explanations
- `recommendations` — preventive action items, completable
- `appointments` — upcoming checkups the user has scheduled
- `health_history` — logged events for the interactive timeline

## Setup

### 1. Install dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# edit .env with your MongoDB URI and a real JWT secret
```

### 3. Start MongoDB

Run a local `mongod`, or point `MONGO_URI` in `.env` at a MongoDB Atlas
cluster.

### 4. Train the ML model (first run only)

```bash
python ml/train_model.py
```

This generates a synthetic, clinically-informed dataset and saves
`ml/risk_model.joblib`. Swap `generate_synthetic_dataset()` in
`train_model.py` for a loader over a real dataset when you have one — the
rest of the pipeline is unchanged. The API will also auto-train on first
request if no model file is found yet.

### 5. Run the app

```bash
python app.py
```

Visit `http://localhost:5000`.

## AI modules

1. **Digital Health Profile** — vitals + lifestyle intake, stored per user.
2. **Future Health Simulation** — transparent, rule-based year-by-year projection of BMI, blood pressure, glucose, and cholesterol.
3. **Disease Risk Prediction** — Random Forest classifier scoring Low / Moderate / High risk with a confidence percentage.
4. **Explainable AI** — ranks the specific factors (age, BMI, smoking, etc.) driving each prediction.
5. **AI Health Coach** — dashboard surface that turns explanations into a prioritized plan.
6. **Preventive Recommendations** — categorized, actionable next steps stored per user.
7. **Interactive Health Timeline** — past history and future projection on one horizon line.

## API testing

Import the routes into Postman (or any REST client) — all `/api/*` routes
except `/api/auth/register` and `/api/auth/login` require an
`Authorization: Bearer <token>` header, obtained from the login/register
response.

## Notes on the ML model

The model ships trained on a **synthetic** dataset built from well-known
directional risk relationships (age, BMI, blood pressure, glucose,
cholesterol, smoking, exercise, sleep, stress, family history). It is meant
to demonstrate the full prediction → explanation → simulation → recommendation
pipeline, not to provide real medical diagnoses. Replace the dataset with
licensed clinical data before using this for anything beyond a demo.
