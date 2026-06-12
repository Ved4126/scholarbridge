# Post-MVP Roadmap

This document outlines the strategic roadmap for the development phases following the MVP. **IMPORTANT:** The features listed below are *future work* and are intentionally excluded from the current MVP release.

## 1. Infrastructure and Persistence
- **PostgreSQL Persistence:** Replace the MVP's volatile in-memory `database.py` with SQLAlchemy models connected to a PostgreSQL database.
- **Redis Cache:** Implement Redis to distribute and persist the scoring cache (`_score_cache`) across multiple worker processes.
- **Logging & Observability:** Integrate structured logging and monitoring (e.g., Datadog, Sentry).

## 2. Platform and UX
- **Frontend App:** Develop a responsive student-facing application using Next.js.
- **Authentication:** Integrate secure user authentication and authorization (e.g., OAuth, JWT).
- **Deployment:** Containerize the application and deploy to a robust cloud infrastructure.

## 3. Data Acquisition
- **Real Scholarship Corpus:** Transition from local development fixtures to a massive, real-world database of scholarships.
- **Scraper / Updater Agent:** Develop an automated data pipeline to scrape, clean, and verify scholarship data on an ongoing basis.
- **Admin Data Curation:** Create internal tooling for admins to curate, approve, and tag incoming scholarships.

## 4. Advanced AI & ML (Phase 2+)
These capabilities will only be introduced *after* the core platform is stable and real user data begins flowing:
- **Vector Search:** Integrate RAG and semantic search utilizing Pinecone or Weaviate.
- **Embeddings:** Utilize advanced embedding models (e.g., BGE-M3 or OpenAI).
- **ML Ranking:** Introduce active Machine Learning (e.g., LightGBM) for dynamic scholarship ranking once sufficient labeled interaction data exists.
- **LangGraph / CrewAI:** Introduce multi-agent orchestration for advanced reasoning only when strictly necessary.
- **RLHF:** Implement Reinforcement Learning from Human Feedback to continuously improve the matching algorithm based on user behavior.
