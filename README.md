# 🔬 LabCast-AI — High-Performance IoT Laboratory Management & RAG Assistant

LabCast-AI is an internal laboratory management system enabling real-time telemetry tracking, machine safety emergency overrides, RAG-assisted document indexing, and technician maintenance scheduling.

This repository contains the complete full-stack environment:
1. **Backend Service (`labcast-ai-backend/`)**: FastAPI + SQLModel + PostgreSQL + MQTT relay + Gemini 2.5 Flash RAG engine.
2. **Web Portal (`frontend/`)**: React + Vite + TS + TanStack Query + TailwindCSS + Shadcn.
3. **Android Client (`LabCastAI/`)**: Jetpack Compose + MVVM + Hilt + Retrofit + WebSockets telemetry sync.

---

## 📖 How It All Works Together (The Story)

Imagine a busy college engineering lab. There are expensive CNC routers, 3D printers, and laser cutters. LabCast-AI connects the **Hardware**, the **Students**, and the **Staff** into one seamless ecosystem. Here is how a typical day flows:

### 1. The Setup (Web Portal & Backend)
The **Lab Admin** logs into the **Web Portal** from their office. They register a new machine (e.g., *CNC Router 01*) and upload its 50-page PDF manual and safety guidelines. The **FastAPI Backend** instantly reads the PDF, extracts the text using OCR, and stores it in a high-dimensional vector database using AI embeddings. 

### 2. The Hardware (ESP32 & MQTT)
A small **ESP32 microcontroller** is wired to the CNC Router's power supply relay. When it turns on, it connects to the lab's Wi-Fi and registers itself with the backend. It starts sending a "heartbeat" every 7 seconds to say *"I am online and my Wi-Fi is good!"* It also listens silently on an MQTT topic for any emergency commands.

### 3. The Student Experience (QR Code & RAG Chat)
A **Student** walks up to the CNC Router to use it. They are confused about how to change the drill bit. Instead of hunting down a technician or a paper manual, they simply pull out their phone and scan the **QR Code** pasted on the machine. 

Their phone browser opens to the **Mobile Chat Interface** (`/chat/CNC01`). They don't even need to log in! They type: *"How do I change the 5mm bit safely?"* The backend's **RAG Engine** (Retrieval-Augmented Generation) instantly searches the 50-page manual, reads the relevant paragraphs, and uses Gemini AI to reply: *"First, ensure the spindle is fully stopped. Then use the 10mm wrench located on the side panel..."* 

### 4. The Emergency Override (Real-Time WebSockets)
Suddenly, the student makes a mistake and the machine starts making a terrible grinding noise! 

Across the room, a **Faculty Member** has the Web Portal open on their laptop. They see the CNC Router card and click the bright red **Emergency Stop** switch. 

In a fraction of a second:
1. The Web Portal tells the Backend.
2. The Backend blasts an emergency payload over **MQTT**.
3. The ESP32 receives the payload and physically cuts the power to the CNC Router.
4. The Backend broadcasts the emergency over **WebSockets**, and instantly, every Admin and Technician looking at the website or their Android app sees a flashing red *!!! EMERGENCY !!!* banner on their screen.

### 5. The Aftermath (Android App & Maintenance)
A **Technician** feels their phone buzz. They open the **LabCast-AI Android App**, authenticate securely, and see the emergency log. They walk over to the machine, fix the jammed drill bit, and clear the emergency from their phone. They then use the app to schedule a maintenance check for next week, and the lab returns to normal.

---

## 🚀 Project Status & Feature Roadmap

| Module | Features | Status |
| :--- | :--- | :--- |
| **Backend API** | RAG Document Ingestion, OCR fallbacks, JWT Auth, RBAC validation, MQTT WebSocket bridge, Audit Logging | **Complete** (Passed 31/31 Pytests) |
| **Web Portal** | Dashboard, Real-time telemetry cards, RAG chatbot interface, Analytics graphs, Maintenance scheduling | **Complete** |
| **Android Client** | Dynamic Server config connection tester, Live WS sync, Approved firmware templates, MQTT OTA triggers, RBAC security gates, Paginated audit log dashboard | **Complete** (Passed 16/16 JVM Tests) |
| **CI/CD** | GitHub Actions workflows for Python, Node, and signed Android release builds | **Complete** |

---

## 📦 Mobile App Signing & Distribution Strategy (Internal College Deployment)

Because LabCast-AI is an internal tool designed for administrative lab-managed tablets and technician devices, it is not distributed via the public Google Play Store. Instead, it utilizes direct enterprise distribution paths:

### 1. Build Verification & Signing
* **Minification:** Enabled R8 minification and resource shrinking in `build.gradle.kts` to optimize footprint.
* **Keystore Security:** Secure signing credentials reside in `secrets/release.keystore` (kept outside version control). Build configurations load these parameters dynamically from `secrets.properties` in production environments.

### 2. Deployment Pathways
1. **Enterprise MDM (Mobile Device Management) - Recommended:** 
   * Laboratory tablets (such as Samsung Knox, Microsoft Intune, or Google Workspace Endpoint Management) are enrolled in the college MDM server.
   * Admins push the signed release APK directly to lab tablets silently.
2. **Manual signed APK Sideloading:**
   * For lab technicians, the signed release APK is hosted on the internal LabCast portal and manually downloaded/installed onto devices with "Install from Unknown Sources" toggled.
