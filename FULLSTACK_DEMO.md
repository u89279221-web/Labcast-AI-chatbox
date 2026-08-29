# LabCast AI Full-Stack End-to-End Demo & Verification (Phase 18.9)

This document records the end-to-end UI verification script and checklist for the full-stack LabCast AI system, covering the browser frontend, FastAPI backend, PostgreSQL database, RAG chatbot engine, WebSocket live notifications, and role-based access control.

---

## Verification Checklist & Execution Steps

### 1. Role-Based Navigation & Access Control
- [x] **Admin Login** (`admin@labcast.edu` / `admin123`):
  - Sidebar shows: **Dashboard**, **Machines**, **Documents**, **IoT Devices**, **Maintenance**, **Analytics**, **Settings**.
- [x] **Faculty Login** (`faculty@labcast.edu` / `faculty123`):
  - Sidebar shows: **Dashboard**, **Machines**, **Documents**.
  - Admin/Technician routes (`/analytics`, `/devices`, `/maintenance`) are blocked and redirect gracefully.
- [x] **Technician Login** (`tech@labcast.edu` / `tech123`):
  - Sidebar shows: **Dashboard**, **Machines**, **IoT Devices**, **Maintenance**.
- [x] **Student Login** (`student@labcast.edu` / `student123`):
  - Sidebar shows: **Dashboard**.
  - Restricted to read-only views and chatbot interaction.

---

### 2. Live SOP Editing & Persistence
- [x] Log in as Admin or Faculty and navigate to Machine Detail (`/machines/CNC01`).
- [x] Modify or add an SOP step (e.g., `"E2E Verification Step: Ensure coolant level is topped up"`).
- [x] Click **Save Changes**. Confirm success toast message appears.
- [x] Refresh the browser page (`F5`) to confirm changes persist in PostgreSQL and render correctly.

---

### 3. Live Emergency Shutdown & WebSocket Toast Notifications
- [x] Navigate to Machine Detail (`/machines/CNC01`).
- [x] Click the **Emergency Shutdown** toggle button.
- [x] Confirm that a destructive red emergency Toast notification fires immediately across all connected browser tabs via the live WebSocket relay (`ws://localhost:8001/ws/events`).
- [x] Confirm the machine status badge updates live to **EMERGENCY ACTIVE**.

---

### 4. Machine-Scoped Chatbot & Manual Source Isolation
- [x] Open chat for **HAAS VF-2 CNC Milling Machine** (`/machines/CNC01/chat`).
  - Query: *"How do I turn on the spindle?"*
  - Answer verifies G-code instructions or spindle startup from CNC manual.
  - Source snippet box displays relevant text chunk strictly from `CNC01` manual.
- [x] Open chat for **South Bend Lathe** (`/machines/LATHE02/chat`).
  - Query: *"What is the chuck key safety rule?"*
  - Source snippet box displays text strictly from `LATHE02` manual without cross-contamination.

---

### 5. Document Ingestion Pipeline
- [x] Log in as Admin/Faculty and navigate to Documents tab on `/machines/CNC01`.
- [x] Drag & drop or select a PDF document file.
- [x] Confirm upload progress bar finishes and document displays an **Extracted** status chip.
- [x] Query the chatbot regarding the new document contents to confirm retrievability in vector search.

---

### 6. Technician Maintenance Logging
- [x] Log in as Technician (`tech@labcast.edu`) and navigate to `/maintenance`.
- [x] Click **Log Maintenance**, select machine `CNC01`, set description to `"Spindle belt alignment"`, and set `Next Due At` within 5 days.
- [x] Save record and verify it is automatically highlighted under **Upcoming Maintenance (Next 7 Days)**.

---

### 7. Admin Analytics Dashboard & Audit Log
- [x] Log in as Admin (`admin@labcast.edu`) and navigate to `/analytics`.
- [x] Verify **Active Devices** count stat card.
- [x] Verify **Chats by Machine** Recharts Bar Chart reflects chatbot interactions.
- [x] Verify **Emergency Activations** Recharts Area Chart reflects time-series event data.
- [x] Verify **Audit Log Table** lists all actions performed above with user IDs and timestamps.

---

### 8. Unauthenticated Mobile QR Chat Flow
- [x] Open a mobile browser or phone camera to `http://<local-ip>:3000/student-chat?machine=CNC01`.
- [x] Confirm the standalone, mobile-optimized chat interface loads cleanly without requiring login.
- [x] Ask a question and confirm complete interactive response.

---

---
Login Credentials
Admin: admin@labcast.edu / admin123
Faculty: faculty@labcast.edu / faculty123
Technician: tech@labcast.edu / tech123
Student: student@labcast.edu / student123
---
## Conclusion
Full-stack software implementation is 100% complete and verified end-to-end via UI workflows and automated testing. Ready for physical ESP32 Hardware Integration.
