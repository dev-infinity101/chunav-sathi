# Chunav Saathi | चुनाव साथी

> AI-powered bilingual election assistant for Indian voters — built for a 6-hour hackathon.

<!-- Demo URL, Lighthouse badge, and coverage badge added in Prompt 10 -->

## Architecture

<!-- Mermaid diagram from PRD added in Prompt 10 -->

## 7 Google Services

| # | Service | Role |
|---|---------|------|
| 1 | Cloud Run | Hosts the full stack (FastAPI + React) |
| 2 | Vertex AI / Gemini 2.5 Flash | Conversational AI with native Hindi |
| 3 | Secret Manager | Stores API keys — zero secrets in code |
| 4 | Firestore | Persists anonymous chat sessions |
| 5 | Cloud Translation API | Localizes static UI strings to Hindi |
| 6 | Cloud Build | CI/CD — auto-deploy on every git push |
| 7 | Cloud Logging + Monitoring | Structured JSON logs, error alerts |

## Run locally

```bash
cd backend && pip install -e ".[dev]"
uvicorn app.main:app --reload
```

```bash
cd frontend && npm install && npm run dev
```

## Deploy

```bash
gcloud builds submit --config cloudbuild.yaml --substitutions=_REGION=asia-south1
```
