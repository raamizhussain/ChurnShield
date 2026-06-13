# ChurnShield Enterprise System Architecture Manifest

## 1. Relational Warehousing & Storage Layer
* **Database Engine:** PostgreSQL
* **Dimension Schema:** Slowly Changing Dimensions (SCD Type 2) tracking validity timelines (`valid_from`, `valid_to`, `is_current`).
* **Fact Layer:** `fact_customer_activity` tracking high-volume event telemetry logs mapped to dimension surrogates.
* **Performance Optimization:** Composite multi-column B-Tree indexes applied across key lookup and timeline fields.

## 2. Ingestion & Feature Engineering Pipeline
* **Idempotency Model:** Watermark-driven checkpoint tracking to prevent duplicate execution side effects.
* **Mathematical Models:** Short-vs-Long window variance checking comparing immediate 3-day velocity patterns against 14-day baselines.
* **External Data Integration:** Competitor market sentiment metrics calculated alongside usage drop rates.

## 3. Serving & Low-Latency API Layer
* **Web Framework:** FastAPI (ASGI Server Process via Uvicorn).
* **Endpoints:** Secure `/predict/uplift` payload validation structures handled by Pydantic.
* **Caching Strategy:** Cache-Aside optimization pattern targeting Redis clusters to reduce API lookup latencies to sub-2ms.

## 4. Automation & Alert Dispatching
* **Orchestration Engine:** Centralized subprocess execution runner managing strict file execution boundaries.
* **CRM Integration Routing:** Automated generation of P0 JSON tracking objects based on high-friction thresholds.