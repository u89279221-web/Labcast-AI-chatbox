# 🧪 LabCast-AI — Local Testing & Quick Start Guide

This guide is designed for teammates to quickly spin up the entire **LabCast-AI** stack locally for development, testing, and hardware integration.

---

## 1. Local Environment Setup

To run the complete system on your machine, you need three terminal windows: one for the Backend, one for the Web Portal, and Android Studio for the Companion App.

### 🟢 A. Start the Backend (FastAPI + PostgreSQL)
1. **Open a terminal** and navigate to the backend folder:
   ```bash
   cd labcast-ai-backend
   ```
2. **Set up the virtual environment & install dependencies** (if not already done):
   ```bash
   python -m venv venv
   .\venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```
3. **Configure Environment Variables**:
   Ensure you have a `.env` file in the `labcast-ai-backend` folder with at least:
   ```env
   DATABASE_URL="sqlite:///./labcast.db"  # Or your PostgreSQL URL
   GEMINI_API_KEY="your_gemini_api_key"
   MQTT_BROKER_HOST="127.0.0.1"           # Optional, for hardware pub/sub
   ```
4. **Run the server**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
   ```
   *The backend API will be available at: http://localhost:8001*

### 🔵 B. Start the Web Portal (React + Vite)
1. **Open a second terminal** and navigate to the frontend folder:
   ```bash
   cd frontend
   ```
2. **Install dependencies** (first time only):
   ```bash
   npm install
   ```
3. **Run the development server**:
   ```bash
   npm run dev -- --host
   ```
   *The Web Portal will be available at: http://localhost:3000*

### 📱 C. Run the Android Companion App
1. **Open Android Studio** and select the `LabCastAI/` folder.
2. Wait for Gradle to sync.
3. **Run the App** on an emulator or a physical device connected via USB.
4. **Important Step on First Launch:**
   * Go to the **Server Config** screen.
   * Set the **Backend API URL** to `http://10.0.2.2:8001` (if using an emulator) or your computer's local IP address (e.g., `http://192.168.1.50:8001`) if using a physical device on the same Wi-Fi.

---

## 2. Seeded Test Credentials

The database is pre-seeded with test accounts representing different role levels. Use these to log in to both the **Web Portal** and the **Android App** to test role-based access control (RBAC).

| Role | Email | Password | What they can test |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@labcast.edu` | `admin123` | Full access. Create machines, toggle emergencies, view audit logs. |
| **Faculty** | `faculty@labcast.edu` | `faculty123` | Configure machines, upload RAG documents, toggle emergencies. |
| **Technician**| `tech@labcast.edu` | `tech123` | View device health, trigger OTA updates, schedule maintenance. |
| **Student** | `student@labcast.edu` | `student123` | Public RAG chat interface only. |

---

## 3. Testing Real-Time Hardware Features (Without Real ESP32s)

You don't need real ESP32 hardware to test the MQTT emergency and configuration workflows. We have a Python simulator!

1. **Log in as Admin** on the Web Portal (`http://localhost:3000`).
2. **Create a test machine** (e.g., Machine ID: `CNC01`).
3. **Open a third terminal** and run the simulator script:
   ```bash
   cd labcast-ai-backend
   python scripts/simulate_esp32.py --machine CNC01 --url http://127.0.0.1:8001 --mqtt
   ```
4. **Test the flow**:
   * Go back to the Web Portal dashboard and toggle the **Emergency Switch** for `CNC01`.
   * Look at the simulator terminal: you will instantly see an `!!! EMERGENCY ACTIVE !!!` alert printed.
   * Log into the **Android App** as Technician/Admin and navigate to Devices. You will see `ESP32-CNC01` sending live heartbeats!

---

## 4. Useful Links

* **Backend Interactive Swagger Docs**: http://localhost:8001/docs
* **Standalone Student Chat UI**: http://localhost:3000/chat/CNC01
* **Full Architecture & Hardware Guide**: See `PROJECT_OVERVIEW.md` in the root folder.
