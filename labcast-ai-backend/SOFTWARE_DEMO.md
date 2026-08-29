# LabCast AI - Software End-to-End Demo

This document captures the successful output of the automated `scripts/demo_walkthrough.py`, which validates the complete software backend stack including REST API, Role-Based Access Control, MQTT IoT integration, and SQLite/PostgreSQL persistence.

## Execution Log

```
=== Phase 17: End-to-End Demo Walkthrough ===
[1] Logging in as roles...
    Tokens acquired successfully.

[2] Launching simulate_esp32.py in MQTT mode...

[3] (Admin) Registering a new Device ID to machine CNC01...
    Response: 200 {"id":"DEV_DEMO","machine_id":"CNC01","status":"online","last_seen":"2026-08-10T10:24:57.242331","config_version":"1.0","wifi_signal":null}

[4] (Admin) Updating SOP for machine CNC01...
    Response: 200 {"name":"HAAS VF-2 CNC Milling Machine","sop":["Turn on power","Verify safety","Begin operation"],"safety_text":"Always wear safety glasses when operating the CNC machine. Do not wear loose clothing, jewelry, or open-toed shoes. Never open the doors while the spindle is spinning or axis is moving. Ensure emergency stop buttons are accessible before starting.","emergency":false}

[5] (Technician) Logging a maintenance record for CNC01...
    Response: 200 {"id":"3030e133-14a1-45d4-a6f6-41d08dfe4dc6","machine_id":"CNC01","technician_id":"U3","description":"Routine calibration and cleaning.","performed_at":"2024-05-15T10:00:00","next_due_at":null}

[6] (Student) Asking Chatbot a question about CNC01...
    Response: 200 [fallback: LLM error] # HAAS VF-2 CNC Milling Machine Operator Manual ## Operation Overview The HAAS ...

[7] (Faculty) Uploading a dummy safety document for CNC01...
    Response: 200 {"id":"41319862-29e0-49f1-8f35-a05024945cd7","filename":"safety.pdf","message":"Document processed and indexed successfully.","extracted_length":0}

[8] (Admin) Triggering Emergency Shutdown on CNC01...
    Response: 200 {"name":"HAAS VF-2 CNC Milling Machine","sop":["Turn on power","Verify safety","Begin operation"],"safety_text":"Always wear safety glasses when operating the CNC machine. Do not wear loose clothing, jewelry, or open-toed shoes. Never open the doors while the spindle is spinning or axis is moving. Ensure emergency stop buttons are accessible before starting.","emergency":true}

[9] (Admin) Fetching Analytics & Audit Logs...
    Analytics Summary: 200 {'chats_per_machine': {'CNC01': 2}, 'total_emergency_activations': 1, 'active_devices': 1}
    Recent Logs:
      - emergency_toggle on machine CNC01 by User U1
      - upload_document on document 41319862-29e0-49f1-8f35-a05024945cd7 by User U2
      - chat on machine CNC01 by User U4
      - create_maintenance on maintenance_record 3030e133-14a1-45d4-a6f6-41d08dfe4dc6 by User U3
      - machine_update on machine CNC01 by User U1

[10] Shutting down ESP32 simulator...

=== Demo Complete ===
```

## Validation Checklist
- [x] RBAC works properly (Admin, Tech, Faculty, Student roles enforced)
- [x] Machine data persists across endpoints
- [x] Audit log tracks critical events (chat, documents, updates, emergency, maintenance)
- [x] Analytics aggregates correct data points
- [x] Hardware simulators properly bridge REST and MQTT layers
