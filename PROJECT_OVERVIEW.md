# 🚀 LabCast-AI — Full-Stack Technical Overview & Architecture Guide

This document provides a **comprehensive technical overview** of the entire LabCast-AI codebase — architecture, data flow, every API endpoint, MQTT topic, file structure, testing, hardware integration, and deployment. Share this with any teammate to get them up to speed quickly.

---

## Table of Contents

1. [Project High-Level Architecture](#1-project-high-level-architecture)
2. [Technology Stack & Key Libraries](#2-technology-stack--key-libraries)
3. [Repository File Structure](#3-repository-file-structure)
4. [Backend API — Complete Endpoint Reference](#4-backend-api--complete-endpoint-reference)
5. [Authentication & RBAC System](#5-authentication--rbac-system)
6. [RAG Document Ingestion & Chat System](#6-rag-document-ingestion--chat-system)
7. [MQTT & Real-Time Communication Architecture](#7-mqtt--real-time-communication-architecture)
8. [Hardware (ESP32) Integration Guide](#8-hardware-esp32-integration-guide)
9. [WebSocket Live Events Bridge](#9-websocket-live-events-bridge)
10. [Web Portal (Frontend)](#10-web-portal-frontend)
11. [Android Companion App](#11-android-companion-app)
12. [Testing Strategy & How to Run Tests](#12-testing-strategy--how-to-run-tests)
13. [Environment Setup & Running Locally](#13-environment-setup--running-locally)
14. [App Signing, CI/CD & Distribution](#14-app-signing-cicd--distribution)
15. [Seeded Test Accounts](#15-seeded-test-accounts)

---

## 1. Project High-Level Architecture

**LabCast-AI** is a full-stack, real-time IoT laboratory management system with a **RAG (Retrieval-Augmented Generation)** AI assistant, machine safety controls, document ingestion, maintenance tracking, OTA firmware management, and an analytics engine.

```
 ┌────────────────────────────┐    ┌────────────────────────────┐
 │  Web Portal (React+Vite)  │    │   Android App (Compose)    │
 │     Port 3000             │    │   Hilt + Retrofit + MVVM   │
 └──────────┬────────┬───────┘    └──────────┬────────┬────────┘
            │ REST   │ WebSocket             │ REST   │ WebSocket
            │ API    │ /ws/events            │ API    │ /ws/events
            ▼        ▼                       ▼        ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │                    Backend (FastAPI)  Port 8001                   │
 │  ┌──────────────┐ ┌──────────────┐ ┌───────────┐ ┌────────────┐ │
 │  │ Auth (JWT)   │ │ RAG Engine   │ │ MQTT-WS   │ │ Audit Log  │ │
 │  │ + RBAC       │ │ Gemini 2.5   │ │ Bridge    │ │ + Analytics│ │
 │  └──────────────┘ └──────────────┘ └─────┬─────┘ └────────────┘ │
 └────────┬──────────────────────────────────┼──────────────────────┘
          │ SQL                              │ MQTT Pub/Sub
          ▼                                  ▼
 ┌──────────────────┐              ┌──────────────────────┐
 │   PostgreSQL     │              │  Mosquitto Broker    │
 │   Port 5433      │              │  Port 1883           │
 └──────────────────┘              └──────────┬───────────┘
                                              │
                                              ▼
                                   ┌──────────────────────┐
                                   │  ESP32 Hardware      │
                                   │  (Lab Machines)      │
                                   └──────────────────────┘
```

### Data Flow Summary

1. **User** logs in via Web or Android → gets JWT token
2. **Admin/Faculty** creates machines, uploads documents → RAG indexes them
3. **ESP32** boots → calls `POST /api/device/register` → then heartbeats every 7s
4. **ESP32** subscribes to MQTT topics for emergency/config/OTA/commands
5. **Admin** toggles emergency on web → backend publishes to MQTT → ESP32 receives instantly → activates relay shutdown
6. **WebSocket bridge** relays all MQTT events to connected Web/Android clients for live UI updates
7. **Android** can trigger OTA, test messages, device restart — all routed through backend → MQTT → ESP32

---

## 2. Technology Stack & Key Libraries

### Backend (`labcast-ai-backend/`)
| Category | Technology |
|:---|:---|
| Framework | Python, FastAPI + Uvicorn |
| Database | SQLModel (SQLAlchemy) + PostgreSQL + Alembic |
| Auth | OAuth2 Bearer (JWT), `passlib`+`bcrypt`, RBAC (4 roles) |
| Rate Limiting | `slowapi` (10 login/min, 5 register/min, 60 chat/min authenticated) |
| Document Extraction | `pypdf`, `python-docx`, `pytesseract`+`pdf2image` (OCR fallback) |
| AI / RAG | HuggingFace `sentence-transformers/all-MiniLM-L6-v2`, Google Gemini 2.5 Flash |
| Real-Time | `paho-mqtt` bridge + FastAPI WebSockets (`/ws/events`) |

### Frontend (`frontend/`)
| Category | Technology |
|:---|:---|
| Core | React 18, Vite, TypeScript, TailwindCSS, Shadcn UI |
| State | Zustand (Auth Store), TanStack React Query v5 |
| Charts | Recharts (Bar + Area charts) |
| DnD | `react-dropzone` for document uploads |
| Real-Time | Custom `useLiveEvents` WebSocket hook with auto-reconnect |

### Android App (`LabCastAI/`)
| Category | Technology |
|:---|:---|
| Architecture | MVVM + Hilt Dependency Injection |
| UI | Jetpack Compose, Material 3 |
| Networking | Retrofit + OkHttp + OkHttp WebSockets |
| Security | Android Keystore `EncryptedSharedPreferences` |
| Dynamic URLs | Custom `DynamicBaseUrlInterceptor` |

---

## 3. Repository File Structure

```
LabCast-AI/
├── labcast-ai-backend/              # Python FastAPI backend
│   ├── app/
│   │   ├── main.py                  # FastAPI app, lifespan, router registration
│   │   ├── core/
│   │   │   ├── config.py            # Settings: DB URL, MQTT, JWT secret
│   │   │   ├── database.py          # SQLModel engine, session, seed data
│   │   │   ├── security.py          # JWT create/verify, password hashing
│   │   │   ├── deps.py              # RequireRole dependency, get_current_user
│   │   │   ├── audit.py             # log_action() helper
│   │   │   └── limiter.py           # Rate limiter setup
│   │   ├── routers/
│   │   │   ├── auth.py              # POST /api/auth/login, /register, GET /roles
│   │   │   ├── machine.py           # CRUD machines, /emergency, /chat
│   │   │   ├── device.py            # Register, heartbeat, OTA, firmware templates
│   │   │   ├── document.py          # Upload, list, delete documents
│   │   │   ├── maintenance.py       # Maintenance schedule CRUD
│   │   │   ├── analytics.py         # Summary stats, audit logs
│   │   │   └── ws.py                # WebSocket /ws/events + MQTT bridge
│   │   ├── models/                  # SQLModel DB models (Machine, Device, User, etc.)
│   │   ├── schemas/                 # Pydantic request/response schemas
│   │   ├── chatbot/
│   │   │   ├── chat.py              # RAG query pipeline
│   │   │   ├── embeddings.py        # Vector embedding + cosine search
│   │   │   └── ingest.py            # PDF/DOCX/OCR text extraction
│   │   └── mqtt/
│   │       └── publisher.py         # publish_message() to MQTT broker
│   ├── scripts/
│   │   └── simulate_esp32.py        # ESP32 hardware simulator
│   ├── tests/                       # 31 pytest tests
│   ├── requirements.txt
│   └── .env                         # Environment variables (not committed)
│
├── frontend/                        # React + Vite web portal
│   ├── src/
│   │   ├── pages/                   # Dashboard, Machines, Analytics, Maintenance
│   │   ├── components/              # RoleGate, GlobalEmergencyListener, etc.
│   │   ├── hooks/                   # useLiveEvents (WebSocket)
│   │   └── stores/                  # Zustand auth store
│   └── package.json
│
├── LabCastAI/                       # Android Companion App
│   ├── app/src/main/java/edu/labcast/app/
│   │   ├── LabCastApplication.kt    # Hilt Application entry
│   │   ├── data/
│   │   │   ├── local/TokenManager.kt         # Encrypted JWT storage
│   │   │   └── remote/
│   │   │       ├── ApiService.kt             # Retrofit API interface
│   │   │       ├── DeviceSyncManager.kt      # WebSocket + REST polling
│   │   │       └── DynamicBaseUrlInterceptor.kt
│   │   ├── di/NetworkModule.kt               # Hilt DI providers
│   │   └── ui/
│   │       ├── MainActivity.kt               # Navigation host
│   │       ├── login/                         # Login screen + ViewModel
│   │       ├── home/                          # Dashboard screen
│   │       ├── devices/                       # Device list + detail screens
│   │       ├── firmware/                      # OTA firmware templates
│   │       ├── security/                      # RBAC, audit log, device revocation
│   │       ├── settings/                      # Server config + connection tester
│   │       └── theme/                         # Material 3 theme
│   ├── app/src/test/                          # 16 JVM unit tests
│   ├── app/build.gradle.kts                   # Build config, signing, R8
│   ├── secrets.properties                     # Keystore path (git-ignored)
│   └── app/proguard-rules.pro
│
├── .github/workflows/ci.yml        # GitHub Actions CI pipeline
├── docker-compose.yml               # Production Docker setup
├── README.md                        # Project summary + roadmap
└── PROJECT_OVERVIEW.md              # THIS FILE
```

---

## 4. Backend API — Complete Endpoint Reference

Base URL: `http://localhost:8001`

### Authentication (`/api/auth`)
| Method | Endpoint | Auth | Description |
|:---|:---|:---|:---|
| `POST` | `/api/auth/register` | None | Register new user (rate: 5/min) |
| `POST` | `/api/auth/login` | None | OAuth2 login, returns JWT (rate: 10/min) |
| `GET` | `/api/auth/roles` | None | Returns RBAC permissions matrix |

### Machines (`/api/machine`)
| Method | Endpoint | Auth | Description |
|:---|:---|:---|:---|
| `GET` | `/api/machine/` | None | List all machines |
| `GET` | `/api/machine/{machine_id}/config` | None | Get machine config (SOP, safety, emergency) |
| `POST` | `/api/machine/{machine_id}/update` | Admin/Faculty | Update SOP/safety text |
| `POST` | `/api/machine/{machine_id}/emergency` | Admin/Faculty/Tech | Toggle emergency flag |
| `POST` | `/api/machine/{machine_id}/chat` | Any (rate limited) | RAG chat query |

### Documents (`/api/machine/{machine_id}/documents`)
| Method | Endpoint | Auth | Description |
|:---|:---|:---|:---|
| `POST` | `/api/machine/{machine_id}/documents` | Admin/Faculty | Upload PDF/DOCX/TXT |
| `GET` | `/api/machine/{machine_id}/documents` | Any | List documents |
| `DELETE` | `/api/machine/{machine_id}/documents/{doc_id}` | Admin/Faculty | Delete + reindex |

### Devices (`/api/device`)
| Method | Endpoint | Auth | Description |
|:---|:---|:---|:---|
| `POST` | `/api/device/register` | None | ESP32 registers on boot |
| `POST` | `/api/device/{device_id}/heartbeat` | None | ESP32 heartbeat (every 7s) |
| `GET` | `/api/device/` | Admin/Tech | List all devices with online/offline status |
| `GET` | `/api/device/{device_id}/status` | Admin/Tech | Single device status |
| `POST` | `/api/device/{device_id}/test-message` | Admin/Tech | Send test MQTT ping |
| `POST` | `/api/device/{device_id}/restart` | Admin/Tech | Remote restart via MQTT |
| `POST` | `/api/device/{device_id}/ota` | Admin/Tech | Trigger OTA firmware update |
| `DELETE` | `/api/device/{device_id}` | Admin only | Revoke/delete device |
| `GET` | `/api/device/firmware/templates` | Admin/Tech/Faculty | List firmware templates |

### Maintenance (`/api/maintenance`)
| Method | Endpoint | Auth | Description |
|:---|:---|:---|:---|
| `GET` | `/api/maintenance/` | Admin/Tech | List maintenance records |
| `POST` | `/api/maintenance/` | Admin/Tech | Create maintenance record |
| `PUT` | `/api/maintenance/{id}` | Admin/Tech | Update maintenance record |
| `DELETE` | `/api/maintenance/{id}` | Admin | Delete maintenance record |

### Analytics (`/api/analytics`)
| Method | Endpoint | Auth | Description |
|:---|:---|:---|:---|
| `GET` | `/api/analytics/summary` | Admin | Chats/machine, emergencies, active devices |
| `GET` | `/api/analytics/logs?limit=50` | Admin | Paginated audit log |

### WebSocket
| Endpoint | Auth | Description |
|:---|:---|:---|
| `ws://host:8001/ws/events?token=JWT` | JWT in query param | Live MQTT event stream |

---

## 5. Authentication & RBAC System

### How Login Works
1. Client sends `POST /api/auth/login` with `username` (email) and `password` as form data
2. Backend verifies password hash (bcrypt), creates JWT containing `{sub: user_id, email, role}`
3. JWT expires after 1440 minutes (24 hours)
4. All subsequent requests include `Authorization: Bearer <token>` header

### Role Permissions Matrix

| Permission | Admin | Faculty | Technician | Student |
|:---|:---:|:---:|:---:|:---:|
| Manage Users | ✅ | ❌ | ❌ | ❌ |
| Manage Devices | ✅ | ❌ | ❌ | ❌ |
| Trigger OTA Updates | ✅ | ✅ | ✅ | ❌ |
| View Audit Logs | ✅ | ❌ | ❌ | ❌ |
| Configure Machines | ✅ | ✅ | ❌ | ❌ |
| File Uploads | ✅ | ✅ | ❌ | ❌ |
| View Devices | ✅ | ❌ | ✅ | ❌ |
| Maintenance Records | ✅ | ❌ | ✅ | ❌ |
| Restart Devices | ✅ | ❌ | ✅ | ❌ |
| Public Chat | ✅ | ✅ | ✅ | ✅ |

### Backend Enforcement
```python
# In router endpoint:
@router.get("/", dependencies=[Depends(RequireRole(["admin", "technician"]))])
```

### Frontend Enforcement
```tsx
<RoleGate allowedRoles={['admin', 'faculty']}>
  <SensitiveComponent />
</RoleGate>
```

---

## 6. RAG Document Ingestion & Chat System

### How Document Upload → AI Chat Works

```
 PDF/DOCX Upload
       │
       ▼
 ┌─────────────────┐
 │  ingest.py       │  Extract text (pypdf / python-docx)
 │                  │  If text < 50 chars/page → OCR fallback (pytesseract)
 └────────┬────────┘
          │ Raw text
          ▼
 ┌─────────────────┐
 │  PostgreSQL      │  Store Document row with extracted_text
 │  Document table  │  + extraction_method ("Standard" or "OCR")
 └────────┬────────┘
          │
          ▼
 ┌─────────────────┐
 │ embeddings.py    │  Chunk text (250 words/chunk)
 │ reindex_machine()│  Generate embeddings (all-MiniLM-L6-v2)
 │                  │  Store in-memory per machine_id
 └────────┬────────┘
          │
    ──── Chat Query ────
          │
          ▼
 ┌─────────────────┐
 │  chat.py         │  Cosine similarity → top 3 chunks
 │  process_chat()  │  Build RAG prompt → Gemini 2.5 Flash
 │                  │  Return answer + source_snippet citation
 └─────────────────┘
```

### Key Implementation Files
- **Text Extraction:** `labcast-ai-backend/app/chatbot/ingest.py`
- **Embedding & Search:** `labcast-ai-backend/app/chatbot/embeddings.py`
- **RAG Chat Pipeline:** `labcast-ai-backend/app/chatbot/chat.py`

---

## 7. MQTT & Real-Time Communication Architecture

### How Real-Time Works End-to-End

```
 Admin toggles Emergency ON (Website)
       │
       ▼
 POST /api/machine/CNC01/emergency  { "emergency": true }
       │
       ├──► PostgreSQL: Machine.emergency = true
       │
       └──► publisher.py: publish_message("labcast/CNC01/emergency", {"emergency": true})
                │
                ▼
         Mosquitto Broker (port 1883)
                │
                ├──► ESP32 (subscribed to labcast/CNC01/emergency)
                │    → Activates hardware shutdown relay
                │
                └──► ws.py MQTT Bridge (subscribed to labcast/#)
                     → Broadcasts to all WebSocket clients
                     → Website shows toast notification
                     → Android app updates device status card
```

### Complete MQTT Topic Map

| Topic Pattern | Direction | Payload | When Published |
|:---|:---|:---|:---|
| `labcast/{machine_id}/emergency` | Backend → ESP32 | `{"emergency": true/false}` | Admin toggles emergency |
| `labcast/{machine_id}/config` | Backend → ESP32 | `{"name", "sop", "safety_text", "emergency"}` | Admin updates machine config |
| `labcast/device/{device_id}/test` | Backend → ESP32 | `{"event": "test_ping", "timestamp": ...}` | "Send Test Message" button |
| `labcast/device/{device_id}/command` | Backend → ESP32 | `{"command": "restart", "timestamp": ...}` | "Restart Device" button |
| `labcast/device/{device_id}/ota` | Backend → ESP32 | `{"download_url", "sha256", "version", "timestamp"}` | "Deploy" OTA button |

### Publisher Implementation
File: `labcast-ai-backend/app/mqtt/publisher.py`
- Uses `paho.mqtt.publish.single()` for fire-and-forget publishing
- Fails silently (logs warning) if broker is unreachable — REST remains source of truth
- Supports optional username/password authentication

---

## 8. Hardware (ESP32) Integration Guide

### What the ESP32 Firmware Must Do

#### Step 1: Register on Boot
```
POST http://<backend-ip>:8001/api/device/register
Body: { "id": "ESP32-CNC01", "machine_id": "CNC01", "firmware_version": "v1.0.0" }
```
- `machine_id` must already exist in the database (create via web portal)
- `id` format convention: `ESP32-{MACHINE_ID}`

#### Step 2: Heartbeat Loop (Every 7 Seconds)
```
POST http://<backend-ip>:8001/api/device/ESP32-CNC01/heartbeat
Body: { "config_version": "1.0", "wifi_signal": -65 }
```
- `wifi_signal` = `WiFi.RSSI()` value
- If no heartbeat for **15 seconds**, backend marks device as **offline**

#### Step 3: Poll Machine Config (Every 7 Seconds)
```
GET http://<backend-ip>:8001/api/machine/CNC01/config
Response: { "name": "CNC Machine 01", "sop": [...], "safety_text": "...", "emergency": false }
```
- Check `emergency` field — if `true`, activate hardware shutdown relays
- This is the **fallback** in case MQTT messages are missed

#### Step 4: Subscribe to MQTT Topics
Connect to the MQTT broker and subscribe to:
```
labcast/{machine_id}/emergency     → Instant emergency on/off
labcast/{machine_id}/config        → Real-time config updates
labcast/device/{device_id}/test    → Test ping (flash LED)
labcast/device/{device_id}/command → Remote restart (ESP.restart())
labcast/device/{device_id}/ota     → OTA firmware download URL + SHA-256
```

### OTA Update Flow
```
 Android App: Select firmware template → Tap "Deploy"
       │
       ▼
 POST /api/device/ESP32-CNC01/ota  { "template_id": "full" }
       │
       ▼
 Backend publishes to MQTT:
   Topic: labcast/device/ESP32-CNC01/ota
   Payload: {
     "download_url": "http://10.0.2.2:8001/static/firmware/full.bin",
     "sha256": "abc123...",
     "version": "2.0.0"
   }
       │
       ▼
 ESP32 receives OTA message:
   1. Download binary from download_url (HTTPS)
   2. Verify SHA-256 hash matches
   3. Flash to OTA partition (Update.h library)
   4. Reboot
```

### Available Firmware Templates
| ID | Name | Version | Components |
|:---|:---|:---|:---|
| `basic` | LabCast Basic | 1.0.0 | Core, Wi-Fi |
| `mqtt` | LabCast +MQTT | 1.1.0 | Core, Wi-Fi, MQTT |
| `tft` | LabCast +TFT | 1.2.0 | Core, Wi-Fi, MQTT, TFT Display |
| `sd` | LabCast +SD | 1.2.1 | Core, Wi-Fi, MQTT, SD Card |
| `full` | LabCast Full | 2.0.0 | Core, Wi-Fi, MQTT, TFT Display, SD Card |

### Reference Simulator
Test without real hardware using:
```bash
cd labcast-ai-backend
python scripts/simulate_esp32.py --machine CNC01 --url http://127.0.0.1:8001 --mqtt
```
This script does **exactly** what real firmware should do — register, heartbeat, poll config, subscribe to MQTT.

### Minimal Arduino Firmware Skeleton
```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

const char* WIFI_SSID     = "LabNetwork";
const char* WIFI_PASS     = "password";
const char* BACKEND_URL   = "http://192.168.1.100:8001";
const char* MQTT_BROKER   = "192.168.1.100";
const int   MQTT_PORT     = 1883;
const char* MACHINE_ID    = "CNC01";
const char* DEVICE_ID     = "ESP32-CNC01";

WiFiClient espClient;
PubSubClient mqttClient(espClient);
HTTPClient http;

void mqttCallback(char* topic, byte* payload, unsigned int length) {
    String msg;
    for (int i = 0; i < length; i++) msg += (char)payload[i];
    StaticJsonDocument<512> doc;
    deserializeJson(doc, msg);
    String topicStr = String(topic);

    if (topicStr.endsWith("/emergency")) {
        if (doc["emergency"].as<bool>()) {
            // >>> ACTIVATE HARDWARE SHUTDOWN RELAYS <<<
        }
    } else if (topicStr.endsWith("/command")) {
        if (doc["command"] == "restart") ESP.restart();
    } else if (topicStr.endsWith("/ota")) {
        String url = doc["download_url"].as<String>();
        // >>> PERFORM OTA UPDATE <<<
    }
}

void setup() {
    Serial.begin(115200);
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    while (WiFi.status() != WL_CONNECTED) delay(500);

    // Register device
    http.begin(String(BACKEND_URL) + "/api/device/register");
    http.addHeader("Content-Type", "application/json");
    http.POST("{\"id\":\"" + String(DEVICE_ID) + "\",\"machine_id\":\"" +
              String(MACHINE_ID) + "\",\"firmware_version\":\"v1.0.0\"}");
    http.end();

    // Connect MQTT
    mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
    mqttClient.setCallback(mqttCallback);
    while (!mqttClient.connected()) { mqttClient.connect(DEVICE_ID); delay(500); }
    mqttClient.subscribe(("labcast/" + String(MACHINE_ID) + "/emergency").c_str());
    mqttClient.subscribe(("labcast/" + String(MACHINE_ID) + "/config").c_str());
    mqttClient.subscribe(("labcast/device/" + String(DEVICE_ID) + "/test").c_str());
    mqttClient.subscribe(("labcast/device/" + String(DEVICE_ID) + "/command").c_str());
    mqttClient.subscribe(("labcast/device/" + String(DEVICE_ID) + "/ota").c_str());
}

void loop() {
    mqttClient.loop();
    static unsigned long lastHB = 0;
    if (millis() - lastHB > 7000) {
        lastHB = millis();
        http.begin(String(BACKEND_URL) + "/api/device/" + DEVICE_ID + "/heartbeat");
        http.addHeader("Content-Type", "application/json");
        http.POST("{\"config_version\":\"1.0\",\"wifi_signal\":" + String(WiFi.RSSI()) + "}");
        http.end();
    }
}
```

---

## 9. WebSocket Live Events Bridge

### How It Works
File: `labcast-ai-backend/app/routers/ws.py`

1. On backend startup, `start_mqtt_bridge()` creates a **background MQTT client** subscribed to `labcast/#`
2. When any MQTT message arrives, the bridge calls `asyncio.run_coroutine_threadsafe()` to broadcast it to all connected WebSocket clients
3. Clients connect via `ws://host:8001/ws/events?token=JWT_TOKEN`
4. Messages arrive as JSON: `{"topic": "labcast/CNC01/emergency", "payload": {"emergency": true}}`
5. Clients send `"ping"` periodically to keep the connection alive; server replies `"pong"`

### Frontend Usage (React)
```tsx
// hooks/useLiveEvents.ts — custom WebSocket hook
const { lastEvent } = useLiveEvents(token);
// lastEvent = { topic: "labcast/CNC01/emergency", payload: { emergency: true } }
```

### Android Usage (Kotlin)
```kotlin
// DeviceSyncManager.kt connects OkHttp WebSocket
// Falls back to REST polling every 10s if WebSocket disconnects
```

---

## 10. Web Portal (Frontend)

### Pages & Features
| Page | Route | Role Required | Features |
|:---|:---|:---|:---|
| Dashboard | `/` | Any | Machine cards with emergency toggle, status badges |
| Machine Detail | `/machines/:id` | Any | SOP editor, document upload, RAG chatbot |
| Chat | `/chat/:id` | None (QR access) | Public chat interface for students via QR code |
| Maintenance | `/maintenance` | Admin/Tech | Schedule and track maintenance records |
| Analytics | `/analytics` | Admin | Charts (chats/machine, emergencies), audit log table |

### Real-Time Features
- **GlobalEmergencyListener.tsx**: App-wide listener that shows toast notifications on emergency events from any machine
- **Live device status**: Device cards update online/offline without page refresh
- **Auto-reconnect**: WebSocket hook automatically reconnects on disconnect

---

## 11. Android Companion App

### Screens
| Screen | Description | Role Required |
|:---|:---|:---|
| Login | JWT auth with encrypted token storage | None |
| Home | Dashboard with quick-action cards | Any |
| Server Config | API URL, MQTT URL, Firmware URL — editable, with "Test Connection" | Any |
| Devices | LazyColumn with live status, heartbeat, Wi-Fi signal | Admin/Tech |
| Device Detail | Full status + "Send Test Message" + "Restart Device" | Admin/Tech |
| Firmware Templates | List of approved firmware packages | Admin/Tech/Faculty |
| OTA Confirmation | Device ID, current vs target version, "Deploy" button | Admin/Tech |
| Security | Auth info, device revocation, role matrix, logout | Admin |
| Audit Log | Paginated system event log, filterable | Admin |

### Key Android Source Files
| File | Purpose |
|:---|:---|
| `data/remote/ApiService.kt` | Retrofit interface for all REST endpoints |
| `data/remote/DeviceSyncManager.kt` | WebSocket connection + REST fallback polling |
| `data/remote/DynamicBaseUrlInterceptor.kt` | Rewrites base URL on-the-fly from config |
| `data/local/TokenManager.kt` | EncryptedSharedPreferences for JWT + server URLs |
| `di/NetworkModule.kt` | Hilt providers for OkHttp, Retrofit, API service |
| `ui/MainActivity.kt` | Navigation host with role-gated routes |

---

## 12. Testing Strategy & How to Run Tests

### Backend Tests (31 tests)
```bash
cd labcast-ai-backend
pytest -v
```
Covers: Auth (login, register, JWT), Machine CRUD, Document upload/delete, Device registration/heartbeat/OTA, RBAC enforcement, Analytics, Audit logging.

### Android JVM Unit Tests (16 tests)
```bash
cd LabCastAI
.\gradlew.bat test
```
Test files:
| Test File | What It Tests |
|:---|:---|
| `LoginViewModelTest.kt` | Login success/failure, token storage |
| `ServerConfigViewModelTest.kt` | Connection testing, URL validation |
| `HomeViewModelTest.kt` | Dashboard data loading |
| `SecurityViewModelTest.kt` | Role matrix loading, device revocation |
| `FirmwareViewModelTest.kt` | Template listing, OTA trigger |
| `DeviceSyncManagerTest.kt` | REST polling, device list updates |

### Frontend Tests
```bash
cd frontend
npm test
```

---

## 13. Environment Setup & Running Locally

### Prerequisites
- Python 3.11+, Node.js 18+, JDK 17
- PostgreSQL (or Docker Compose for all-in-one)
- Mosquitto MQTT broker (optional — system works via REST fallback without it)

### Backend
```powershell
cd labcast-ai-backend

# Create .env file with:
# DATABASE_URL=postgresql://labcast_user:secretpassword@localhost:5433/labcast_db
# GEMINI_API_KEY=your_google_api_key
# MQTT_BROKER_HOST=127.0.0.1  (optional)
# SECRET_KEY=your_production_secret

pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend
```powershell
cd frontend
npm install
npm run dev -- --host
# Runs on http://localhost:3000
```

### Docker Compose (Production)
```bash
docker-compose up -d
# Only add --build if requirements.txt or package.json change
```

### Android
Open `LabCastAI/` in Android Studio → Run on emulator or device.
Configure the backend URL in the Server Configuration screen.

---

## 14. App Signing, CI/CD & Distribution

### Release Signing
- **Keystore:** `secrets/release.keystore` (outside version control)
- **Config:** `LabCastAI/secrets.properties` loads keystore path, passwords
- **R8 Minification:** Enabled in `app/build.gradle.kts` for release builds
- **ProGuard:** `app/proguard-rules.pro` for custom rules

### Build Commands
```bash
cd LabCastAI
.\gradlew.bat test              # Run unit tests
.\gradlew.bat assembleRelease   # Build signed, minified APK
# Output: app/build/outputs/apk/release/app-release.apk
```

### CI/CD Pipeline
File: `.github/workflows/ci.yml`
- **Backend job:** `pytest`
- **Frontend job:** `npm test`
- **Android job:** `./gradlew test` + `./gradlew assembleRelease`

### Distribution Strategy (Internal College Deployment)
This is an internal tool — **NOT** on Google Play Store.
1. **MDM (Recommended):** Push signed APK via Samsung Knox / Microsoft Intune / Google Workspace
2. **Manual Sideload:** Host APK on internal portal, install with "Unknown Sources" enabled

---

## 15. Seeded Test Accounts

These accounts are automatically created on first backend startup:

| Email | Password | Role | Access |
|:---|:---|:---|:---|
| `admin@labcast.edu` | `admin123` | Admin | Full system access |
| `faculty@labcast.edu` | `faculty123` | Faculty | Machines, documents, chat |
| `tech@labcast.edu` | `tech123` | Technician | Devices, maintenance, OTA |
| `student@labcast.edu` | `student123` | Student | Chat only |

---

## Quick Start Checklist for New Teammates

1. ✅ Clone the repository
2. ✅ Start PostgreSQL (or `docker-compose up -d`)
3. ✅ Create `.env` in `labcast-ai-backend/` with DB URL + Gemini API key
4. ✅ Start backend: `uvicorn app.main:app --port 8001`
5. ✅ Start frontend: `npm run dev -- --host` in `frontend/`
6. ✅ Login with `admin@labcast.edu` / `admin123` on `http://localhost:3000`
7. ✅ Create a machine (e.g., `CNC01`) on the Dashboard
8. ✅ Test the ESP32 simulator: `python scripts/simulate_esp32.py --machine CNC01 --url http://127.0.0.1:8001`
9. ✅ Open Android app → Server Config → set backend URL → Login
10. ✅ Toggle emergency on website → verify ESP32 simulator receives it
