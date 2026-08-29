# LabCast AI System

[![Run Tests](https://github.com/your-org/labcast-ai-backend/actions/workflows/tests.yml/badge.svg)](https://github.com/your-org/labcast-ai-backend/actions/workflows/tests.yml)

LabCast AI is a smart laboratory equipment management system. It provides a central API and modern web app to manage machine configurations, Standard Operating Procedures (SOPs), safety protocols, emergency shutdowns, IoT devices, document ingestion, maintenance tracking, and real-time analytics. Additionally, it features a Retrieval-Augmented Generation (RAG) chatbot that allows users to ask highly contextual questions about specific machinery based on the machine's actual manuals.

> **Note on Hardware:** Physical hardware integration is the **LAST** stage of this project's roadmap. Everything up to that point—including the API, Web App, Chat UI, Dashboard, and Admin controls—runs, is fully tested, and can be developed entirely on a local laptop using the provided ESP32 Simulator (`scripts/simulate_esp32.py`).

## Architecture

```text
  [ User Phone / Web App ]   [ Admin & Tech Dashboard ]
             |                           |
             +-------------+-------------+
                           |
                           v
               [ Nginx Reverse Proxy ]
                           |
           +---------------+---------------+
           | (HTTP / REST)                 | (WebSockets)
           v                               v
  [ FastAPI Backend ] <----------> [ WebSocket Relay ]
  |                 |                      ^
  v                 v                      |
[Postgres DB] [Vector Search] <----+ [MQTT Broker]
                                   ^
                                   | (MQTT Pub/Sub)
                          [ ESP32 Simulator ]
```

---

## Quick Start & Setup

### 1. Backend Setup
Create a virtual environment and install dependencies:
```bash
cd labcast-ai-backend
python -m venv venv

# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
python -m scripts.seed
uvicorn app.main:app --reload --port 8001
```
API Documentation is available at `http://localhost:8001/docs`.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Access the application at `http://localhost:3000`.

---

## Testing

### Backend Unit & Integration Tests (Pytest)
```bash
cd labcast-ai-backend
pytest -v
```

### Frontend Unit & Component Tests (Vitest + React Testing Library)
```bash
cd frontend
npm run test -- --run
```

### End-to-End Tests (Playwright)
```bash
cd frontend
npx playwright test
```

Our CI pipeline (GitHub Actions) automatically executes both backend and frontend test suites on every push and pull request.

---

## Full-Stack Deployment via Docker Compose

Run the complete application stack (Nginx Frontend, FastAPI Backend, PostgreSQL Database) with a single command:
```bash
cd labcast-ai-backend
docker-compose up --build
```
This serves the frontend at `http://localhost:3000` with Nginx handling reverse-proxying for `/api/` and `/ws/` to the backend service.

---

## Environment Variables

| Variable | Purpose | Required / Optional |
|---|---|---|
| `GEMINI_API_KEY` | Powers the conversational RAG chatbot using Gemini 3.6 Flash. | **Optional**. If omitted, the chatbot gracefully falls back to returning verbatim manual text chunks. |
| `DATABASE_URL` | Connection URL for PostgreSQL / SQLite database. | Optional (defaults to local SQLite). |

---

## Completed Roadmap & Features

- [x] **Core FastAPI Backend & RAG Pipeline**
- [x] **Device Management & Heartbeats**
- [x] **Real-time MQTT & WebSocket Relay**
- [x] **Authentication & Role-Based Access Control (Admin, Faculty, Technician, Student)**
- [x] **OCR Document Ingestion Pipeline**
- [x] **Audit Logging & Analytics Dashboard**
- [x] **Maintenance Records & Upcoming Schedules**
- [x] **Single-Page Application Frontend (Vite + React, Tailwind CSS, TanStack Query, Recharts)**
- [x] **Containerization & Docker Compose Deployment**
- [ ] **Hardware Integration** *(Full-stack software complete as of Phase 18.9 — verified UI-only end-to-end. Hardware Integration begins next.)*
