# ChurnShield: Multi-Tenant Autonomous Causal AI SaaS Pipeline

ChurnShield is an enterprise-grade SaaS analytics engine that shifts churn management from simple binary prediction to actionable Causal AI optimization. Built as a high-throughput multi-tenant platform, it allows corporate users to drop raw, timestamped customer interaction logs into a secure terminal and instantly receive portfolio-wide financial risk metrics, operational telemetry tables, and high-impact generative retention playbooks.

---

## 🛠️ System Architecture & Workflow



1. **Ingestion & Automated Feature Engineering:** The FastAPI gateway ingests raw, unaggregated activity logs via memory-buffered data streams. A high-performance pandas compilation loop groups actions by customer ID and automatically calculates 7-day vs. 14-day user interaction velocity drops and unresolved support tickets on the fly.
2. **Causal Inference Machine Learning:** Instead of targeting generic high-risk customers, the system utilizes a LightGBM T-Learner uplift modeling structure to isolate the *incremental treatment effect*. This effectively groups accounts into actionable operational cohorts (e.g., separating "Persuadable" targets from "Sure Things").
3. **Agentic LLM Operations Layer:** To optimize platform resource constraints, the engine dynamically extracts the maximum threat signature from the batch dataset and triggers a high-performance Llama-3.1 inference array via Groq to compile a precise, plain-English executive response brief.
4. **Streamlit Enterprise Console:** A clean, minimal front-end interface built to mirror a corporate console gateway—complete with an authentication layout block, batch metrics dashboards, and dynamic multi-column tracking log tables.

---

## 🚀 Tech Stack

- **Backend Gateway:** FastAPI, Uvicorn, Pydantic, Python-Dotenv
- **Analytical Core:** Pandas, NumPy, Scikit-Learn, LightGBM
- **Inference Layer:** Groq SDK, Meta-Llama-3.1-8B-Instant
- **Frontend Dashboard:** Streamlit, Request Routing Arrays

---

## 📂 Repository Blueprint

```text
├── app_saas.py                 # Streamlit multi-step executive interface layout
├── main_api.py                 # FastAPI microservice routing raw log processing
├── llm_explanation_worker.py   # Groq client worker optimizing retention brief text
├── raw_activity_template.csv  # Minimal template structure required for user uploads
├── test_raw_logs.csv           # Mock event-streaming dataset containing 80 database rows
├── requirements.txt            # Unified platform dependency manifest
└── README.md                   # System configuration overview
