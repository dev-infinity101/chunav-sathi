# Chunav Saathi — Dev Checklist
> 6-hour hackathon build tracker. Update as each prompt completes.

---

## Pre-build Setup
- [x] Read PRD + architecture (`chunav-saathi-buildplan.md`)
- [x] Read all 10 prompts (`prompts.md`)
- [ ] GCP project created + APIs enabled
- [ ] Artifact Registry repo created
- [ ] Firestore database created (Native mode)
- [ ] Service account `chunav-runner` created with least-privilege roles
- [ ] `gemini-api-key` stored in Secret Manager
- [ ] Cloud Build trigger connected to GitHub repo

---

## Prompt 1 — Project Scaffold ✅ DONE
- [x] `backend/pyproject.toml` — all deps listed, dev extras separate
- [x] `backend/.python-version` — 3.11
- [x] `backend/conftest.py` — sys.path fix for `pytest backend/tests` from root
- [x] `backend/app/main.py` — FastAPI, CORS, health check `/healthz`, static mount, slowapi
- [x] `backend/app/core/config.py` — pydantic-settings, reads PROJECT_ID / REGION / GEMINI_API_KEY
- [x] `backend/app/core/logging.py` — structured JSON logger (severity field for Cloud Logging)
- [x] `backend/app/core/security.py` — slowapi Limiter singleton
- [x] `backend/app/routers/chat.py` — stub APIRouter
- [x] `backend/app/routers/timeline.py` — stub APIRouter
- [x] `backend/app/routers/eligibility.py` — stub APIRouter
- [x] `backend/app/rag/embed.py` — stub (zero vectors)
- [x] `backend/app/rag/index_builder.py` — stub (creates placeholder FAISS index so Docker build passes)
- [x] `backend/app/rag/retriever.py` — stub (loads index, returns empty list)
- [x] `backend/app/services/gemini.py` — stub async generator
- [x] `backend/app/services/firestore.py` — stub no-ops
- [x] `backend/app/services/secrets.py` — stub env-first fetcher
- [x] `backend/app/models/schemas.py` — empty Pydantic model stubs
- [x] `backend/tests/conftest.py` — empty, ready for Prompt 5
- [x] `backend/tests/test_placeholder.py` — 1 passing smoke test
- [x] `backend/data/.gitkeep` — directory tracked
- [x] `backend/.venv/` — isolated venv created (NOT global install)
- [x] `frontend/package.json` — React 18, Vite, Tailwind 3, Radix UI, react-i18next, react-markdown
- [x] `frontend/vite.config.ts` — Vite config with `/api` proxy to port 8080
- [x] `frontend/tsconfig.json` — strict TypeScript
- [x] `frontend/tsconfig.node.json`
- [x] `frontend/index.html` — semantic, with description meta
- [x] `frontend/tailwind.config.js` — WCAG AA color tokens (all ≥ 4.5:1 contrast verified)
- [x] `frontend/postcss.config.js`
- [x] `frontend/src/main.tsx` — React 18 createRoot
- [x] `frontend/src/App.tsx` — minimal scaffold placeholder
- [x] `frontend/src/index.css` — Tailwind directives + focus-visible + prefers-reduced-motion
- [x] `frontend/src/vite-env.d.ts`
- [x] `frontend/src/locales/en.json` — empty `{}`
- [x] `frontend/src/locales/hi.json` — empty `{}`
- [x] `frontend/src/components/ChatPanel.tsx` — stub
- [x] `frontend/src/components/Timeline.tsx` — stub
- [x] `frontend/src/components/EligibilityForm.tsx` — stub
- [x] `frontend/src/components/LanguageToggle.tsx` — stub
- [x] `frontend/src/components/LevelSelector.tsx` — stub
- [x] `frontend/src/components/VoiceInput.tsx` — stub
- [x] `frontend/src/hooks/useChat.ts` — stub
- [x] `frontend/src/hooks/useI18n.ts` — stub
- [x] `Dockerfile` — multi-stage (frontend-build → backend-build → runtime), non-root user, FAISS baked at build time
- [x] `.dockerignore`
- [x] `cloudbuild.yaml` — build → push SHA + latest → Cloud Run deploy
- [x] `.gitignore` — Python + Node
- [x] `README.md` — stub with 7 GCP services table

### Acceptance gates
- [x] `pytest backend/tests` — 1 passed ✅
- [ ] `npm run build` — needs `npm install` first (not yet run locally)
- [ ] `docker build .` — not yet tested locally

---

## Prompt 2 — Election Knowledge Base ⬜ TODO
- [ ] `backend/data/lok_sabha.yaml` — 10 phases, 15 key concepts, 20 FAQs
- [ ] `backend/data/vidhan_sabha.yaml` — state assembly structure
- [ ] `backend/data/panchayat.yaml` — three-tier, 73rd Amendment context
- [ ] `backend/data/eligibility.yaml` — voter + candidate rules
- [ ] `backend/data/glossary.yaml` — 40+ terms (EVM, VVPAT, NOTA, MCC…)
- [ ] `backend/data/faqs.yaml` — 30 cross-cutting FAQs
- [ ] Acceptance: all 6 files load with `yaml.safe_load` without errors

---

## Prompt 3 — RAG Pipeline ⬜ TODO
- [ ] `backend/app/rag/embed.py` — real `get_embeddings()` via google-genai `text-embedding-004`, batched, L2-normalized
- [ ] `backend/app/rag/index_builder.py` — full YAML → chunks → embed → FAISS IndexFlatIP → save
- [ ] `backend/app/rag/retriever.py` — full retrieve() with level + lang filtering
- [ ] `backend/tests/test_rag.py` — index loads, retrieval relevant, lang/level filtering
- [ ] Acceptance: `python -m app.rag.index_builder` produces `faiss_index/`; `pytest tests/test_rag.py` passes

---

## Prompt 4 — API Endpoints ⬜ TODO
- [ ] `backend/app/services/secrets.py` — real Secret Manager fetch with lru_cache
- [ ] `backend/app/services/gemini.py` — real streaming via google-genai `gemini-2.5-flash`
- [ ] `backend/app/services/firestore.py` — real async Firestore read/write
- [ ] `backend/app/models/schemas.py` — full Pydantic v2 schemas with validators
- [ ] `backend/app/routers/chat.py` — POST `/api/chat` SSE, 30/min rate limit, lang detection, RAG, Firestore persist
- [ ] `backend/app/routers/timeline.py` — GET `/api/timeline/{level}?lang=en|hi`, cached YAML
- [ ] `backend/app/routers/eligibility.py` — POST `/api/eligibility`, pure logic, structured reasoning
- [ ] Wire all routers in `main.py`
- [ ] Acceptance: `/healthz` 200, SSE chat works, `/api/timeline/lok_sabha?lang=hi` returns Hindi names

---

## Prompt 5 — Backend Tests ⬜ TODO
- [ ] `backend/tests/conftest.py` — async test_client, mock_retriever, mock_gemini, mock_firestore fixtures
- [ ] `backend/tests/test_chat.py` — SSE format, rate limit, invalid input, lang detection, grounded context, citations
- [ ] `backend/tests/test_timeline.py` — all 3 levels, 404 on invalid, lang param
- [ ] `backend/tests/test_eligibility.py` — eligible / age < 18 / non-citizen cases
- [ ] `backend/tests/test_rag.py` — extended edge cases
- [ ] Add `--cov=app --cov-report=term --cov-report=html --cov-fail-under=70` to `pyproject.toml`
- [ ] Acceptance: `pytest` passes, coverage ≥ 70%, `htmlcov/` generated

---

## Prompt 6 — Frontend Layout + i18n ⬜ TODO
- [ ] `frontend/src/locales/en.json` — ~80 keys
- [ ] `frontend/src/locales/hi.json` — ~80 keys
- [ ] `frontend/src/hooks/useI18n.ts` — real react-i18next wrapper, persists to localStorage, updates `document.documentElement.lang`
- [ ] `frontend/src/components/LanguageToggle.tsx` — role="switch", aria-checked, keyboard operable
- [ ] `frontend/src/components/LevelSelector.tsx` — Radix RadioGroup, arrow-key navigation
- [ ] `frontend/src/App.tsx` — skip-to-content link, semantic landmarks, two-column layout, mobile stack
- [ ] Acceptance: keyboard tab works end-to-end, lang toggle changes all text, no axe-core violations

---

## Prompt 7 — Chat + Voice ⬜ TODO
- [ ] `frontend/src/hooks/useChat.ts` — real SSE fetch, session persistence, streaming state
- [ ] `frontend/src/components/ChatPanel.tsx` — full chat UI, react-markdown, citations, sample questions, Enter-to-send
- [ ] `frontend/src/components/VoiceInput.tsx` — Web Speech API, graceful fallback, aria-pressed
- [ ] a11y: aria-live="polite", aria-busy, role="alert" for errors, focus management
- [ ] Acceptance: streaming EN + HI responses with citations; voice input in both langs

---

## Prompt 8 — Timeline Component ⬜ TODO
- [ ] `frontend/src/components/Timeline.tsx` — Radix Accordion stepper, fetch `/api/timeline/{level}`, skeleton loading, error retry
- [ ] Reduced-motion respected
- [ ] Acceptance: tab/Enter/Space navigation, screen reader announces "Step N of 10: Phase Name", Lighthouse a11y ≥ 95

---

## Prompt 9 — Eligibility Form + A11y Pass ⬜ TODO
- [ ] `frontend/src/components/EligibilityForm.tsx` — all fields with labels, aria-describedby errors, 28 states + 8 UTs, result card
- [ ] Full accessibility audit: Lighthouse ≥ 95, focus indicators, contrast, reduced-motion, dark mode, lang attributes
- [ ] Acceptance: Lighthouse Accessibility score ≥ 95 (screenshot committed)

---

## Prompt 10 — Deploy + Demo Polish ⬜ TODO
- [ ] Verify Dockerfile multi-stage build locally (`docker build .`)
- [ ] `gcloud builds submit` — successful Cloud Run deploy
- [ ] Smoke test live URL (healthz, chat EN, chat HI, timeline x3, eligibility form)
- [ ] `README.md` — live URL, architecture diagram, GCP table, badges, Lighthouse screenshot
- [ ] Generate coverage badge
- [ ] 90-second Loom recorded and uploaded
- [ ] Submission link confirmed working

---

## Cross-cutting Quality Gates
- [ ] No secrets in code — all via Secret Manager / env vars
- [ ] No synchronous blocking calls in async context
- [ ] SSE never buffered
- [ ] All Python functions type-hinted
- [ ] All TypeScript strict mode passing
- [ ] Rate limiting active (30 req/min per IP)
- [ ] Lighthouse Accessibility ≥ 95
- [ ] Test coverage ≥ 70%
- [ ] Cold start < 5s (FAISS baked in image)
- [ ] FCP < 1.5s on 4G
