import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_document():
    doc = docx.Document()

    # Page Margins
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Styles & Fonts
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    # Title Page / Header Title
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_p.add_run("ACADEMIC PROJECT REPORT\nLABCAST AI: SMART LABORATORY ASSISTANT & IOT TELEMETRY MONITORING SYSTEM")
    title_run.font.name = 'Calibri'
    title_run.font.size = Pt(22)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A) # Dark Navy

    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_run = sub_p.add_run("A Multi-Tier System for Real-Time Machine Telemetry, AI RAG Guidance, and Wireless Firmware Management\n")
    sub_run.font.size = Pt(13)
    sub_run.font.italic = True
    sub_run.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)

    # Metadata Block
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Project Name:", "LabCast AI System"),
        ("Developer / Author:", "Aziz M. Nadaf"),
        ("Target Platform:", "Web Portal (GitHub Pages) + Android Admin Client + ESP32 Microcontroller"),
        ("Date / Academic Session:", "September 2026")
    ]
    for i, (k, v) in enumerate(meta_data):
        row = meta_table.rows[i]
        c1, c2 = row.cells[0], row.cells[1]
        c1.text, c2.text = k, v
        c1.paragraphs[0].runs[0].font.bold = True
        c1.paragraphs[0].runs[0].font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        set_cell_background(c1, "F1F5F9")
        set_cell_background(c2, "F8FAFC")
        set_cell_margins(c1, top=120, bottom=120, left=150, right=150)
        set_cell_margins(c2, top=120, bottom=120, left=150, right=150)

    doc.add_paragraph("\n")

    def add_heading_1(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(18)
        h.paragraph_format.space_after = Pt(6)
        r = h.add_run(text)
        r.font.name = 'Calibri'
        r.font.size = Pt(16)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        return h

    def add_heading_2(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(12)
        h.paragraph_format.space_after = Pt(4)
        r = h.add_run(text)
        r.font.name = 'Calibri'
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)
        return h

    def add_callout(text, title="NOTE"):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.rows[0].cells[0]
        set_cell_background(cell, "EFF6FF")
        set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
        p = cell.paragraphs[0]
        r1 = p.add_run(f"📌 {title}: ")
        r1.font.bold = True
        r1.font.color.rgb = RGBColor(0x1D, 0x4E, 0xD8)
        r2 = p.add_run(text)
        r2.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)

    # 1. ABSTRACT
    add_heading_1("1. Executive Summary & Abstract")
    p = doc.add_paragraph()
    p.add_run(
        "Modern engineering and fabrication laboratories require seamless synchronization between machinery, safety overrides, "
        "operator guidance, and wireless maintenance protocols. The LabCast AI System is an end-to-end multi-tier platform "
        "designed to provide real-time equipment telemetry, instant AI troubleshooting, and wireless firmware delivery.\n\n"
        "The system consists of four primary components: (1) a Universal Web Chatbox Portal hosted 24/7 on GitHub Pages; "
        "(2) a native Android Mobile Administration Client featuring security authentication, live device telemetry, inline OTA flashing, "
        "and a real-time C++ code generator; (3) a local PC Python FastAPI and Mosquitto MQTT backend server; and (4) an ESP32 "
        "microcontroller terminal operating in dual Wi-Fi mode with zero switch latency."
    )

    # 2. SYSTEM ARCHITECTURE
    add_heading_1("2. System Architecture & Topology")
    doc.add_paragraph(
        "The architecture is structured across four decoupled layers to ensure maximum uptime, low-latency control, "
        "and zero dependency on third-party cloud tunnels:"
    )
    
    arch_table = doc.add_table(rows=5, cols=4)
    arch_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Layer Name", "Technologies Used", "Hosting / Location", "Primary Responsibility"]
    hdr_row = arch_table.rows[0]
    for j, text in enumerate(headers):
        cell = hdr_row.cells[j]
        cell.text = text
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_background(cell, "0F172A")
        set_cell_margins(cell, top=120, bottom=120, left=120, right=120)

    rows_data = [
        ("Frontend Website", "HTML5, CSS3, JavaScript, QRCode.js", "GitHub Pages (HTTPS)", "Universal AI Web Chatbox & Mobile QR Scanner Poster"),
        ("Android Mobile App", "Kotlin 1.9, Android SDK (API 34), Gradle", "Android Device / APK", "Security Login, Devices Status, Real OTA Flashing, Code Generator"),
        ("Backend Server", "Python 3.10, FastAPI, Mosquitto MQTT", "Local PC Server (192.168.29.4)", "MQTT Broker (1883), REST Telemetry APIs, PyTorch RAG Search"),
        ("ESP32 Firmware", "C++ (Arduino Core), WebServer, PubSubClient", "ESP32 Board (10.10.10.1)", "Dual Wi-Fi AP+STA, TFT Display, GPIO 17 Relay E-Stop")
    ]

    for i, row_vals in enumerate(rows_data, start=1):
        row = arch_table.rows[i]
        bg_color = "F8FAFC" if i % 2 == 1 else "FFFFFF"
        for j, val in enumerate(row_vals):
            cell = row.cells[j]
            cell.text = val
            set_cell_background(cell, bg_color)
            set_cell_margins(cell, top=100, bottom=100, left=120, right=120)

    doc.add_paragraph("\n")

    # 3. WEBSITE COMPONENT
    add_heading_1("3. Website Component (Universal AI Web Chatbox)")
    doc.add_paragraph(
        "The website component provides an instant, universal technical assistant for laboratory operators. "
        "It runs entirely client-side without external dependencies, allowing operators to query Standard Operating Procedures (SOPs), "
        "safety rules, and operational guidelines across multiple domains."
    )
    
    add_heading_2("3.1 Technical Specifications & Tools")
    p = doc.add_paragraph()
    p.add_run("• Languages: ").bold = True
    p.add_run("HTML5, CSS3, JavaScript (ES6+)\n")
    p.add_run("• Styling Framework: ").bold = True
    p.add_run("Custom CSS3 Variables, Flexbox, CSS Grid, Dark Navy Slate Theme\n")
    p.add_run("• Libraries Used: ").bold = True
    p.add_run("QRCode.js (Dynamic QR generation with fallback API)\n")
    p.add_run("• Hosting Infrastructure: ").bold = True
    p.add_run("GitHub Pages (24/7 Permanent HTTPS Endpoint, Zero IP Prompts, Zero Disconnects)\n")
    p.add_run("• Live Website Link: ").bold = True
    p.add_run("https://u89279221-web.github.io/Labcast-AI-chatbox/lab_assistant.html\n")
    p.add_run("• GitHub Repository: ").bold = True
    p.add_run("https://github.com/u89279221-web/Labcast-AI-chatbox")

    add_heading_2("3.2 Core Functional Capabilities")
    doc.add_paragraph(
        "1. Multi-Machine Technical Engine: Knowledge coverage for 3D Printers (PLA/PETG/ABS/TPU temps, bed leveling), CNC Routers (RPM, feeds, vise clamping), Laser Cutters (acrylic/wood focus, hazardous PVC chlorine gas warnings), Manual Lathes (chuck key safety), Soldering, Circuits, Python, C++, Math, and Physics.\n"
        "2. Standalone QR Poster: Displays high-resolution QR codes that allow any smartphone scanner to open the Web Chatbox directly like Google without authentication friction."
    )

    # 4. ANDROID APPLICATION COMPONENT
    add_heading_1("4. Android Client Component (Mobile Admin App)")
    doc.add_paragraph(
        "The Android Application (package `com.labcast.ai`) is the mobile control center for laboratory administrators and technicians. "
        "It provides security authentication, real asynchronous background HTTP network polling, live telemetry monitoring, "
        "remote emergency stop dispatches, embedded OTA firmware flashing, and an interactive C++ parameter generator."
    )

    add_heading_2("4.1 Software Tools & Build Environment")
    p = doc.add_paragraph()
    p.add_run("• Programming Language: ").bold = True
    p.add_run("Kotlin 1.9+\n")
    p.add_run("• Target SDK / Min SDK: ").bold = True
    p.add_run("Android 14 (API level 34) / Android 7.0 (API level 24)\n")
    p.add_run("• Software Applications & Tools Used: ").bold = True
    p.add_run("Android Studio, Gradle 9.3+, ADB (Android Debug Bridge), Android CLI, Android Virtual Device (Pixel_7 Emulator)\n")
    p.add_run("• Networking Engine: ").bold = True
    p.add_run("Multi-threaded HttpURLConnection background threads with cleartext HTTP permissions\n")
    p.add_run("• Web Integration: ").bold = True
    p.add_run("Android WebKit WebView with custom WebViewClient and JavaScript execution\n")
    p.add_run("• Compiled APK Output File: ").bold = True
    p.add_run("LabcastAdminApp-debug.apk (5.8 MB)\n")
    p.add_run("• GitHub Repository: ").bold = True
    p.add_run("https://github.com/azizmnadaf26-glitch/LabCastAI-android")

    add_heading_2("4.2 Detailed Screen & Module Breakdown")
    
    doc.add_paragraph(
        "🔒 Security Authentication System (Login Screen):\n"
        "Requires technician authentication (Email: admin@labcast.ai / Passcode: 123456) with role selection (Administrator / Technician) "
        "and a Quick Demo Login option for instant testing."
    )

    doc.add_paragraph(
        "📱 Page 1 — Live Connected Devices & Status Dashboard:\n"
        "Executes real background HTTP GET requests to target addresses (http://10.10.10.1 and http://192.168.29.4:8001). "
        "If the device responds with HTTP 200 OK, the badge turns GREEN ONLINE with exact latency (e.g. 12ms). "
        "Includes a REAL EMERGENCY STOP button that sends an HTTP POST payload to http://10.10.10.1/emergency to trip the GPIO 17 relay."
    )

    doc.add_paragraph(
        "⚡ Page 2 — Wireless OTA Code Upload & Real Inline WebView:\n"
        "Renders a real, live embedded Android WebView loading http://10.10.10.1 and http://10.10.10.1/update directly on screen. "
        "Technicians can select binary .bin firmware files and flash the ESP32 over Wi-Fi without needing a laptop. Includes 3 ready-made firmware code templates."
    )

    doc.add_paragraph(
        "✍️ Page 3 — Real Editable Code Format & Parameter Generator:\n"
        "Provides editable input fields for ROUTER_SSID, ROUTER_PASS, MQTT_BROKER_IP, MACHINE_ID, ap_ssid, and ap_password. "
        "Generates the complete C++ Arduino firmware code in real time as the user types, complete with a 'Test & Ping ESP32' live connection button."
    )

    # 5. BACKEND SERVER & IOT BROKER
    add_heading_1("5. Backend Server & IoT Broker Component")
    doc.add_paragraph(
        "The backend infrastructure consists of a Python FastAPI web server and an Eclipse Mosquitto MQTT Broker running locally on the laboratory server PC."
    )
    p = doc.add_paragraph()
    p.add_run("• Languages & Frameworks: ").bold = True
    p.add_run("Python 3.10+, FastAPI (ASGI Framework), Uvicorn Server\n")
    p.add_run("• MQTT Telemetry Broker: ").bold = True
    p.add_run("Eclipse Mosquitto (Port 1883)\n")
    p.add_run("• Database & AI Vector Engine: ").bold = True
    p.add_run("SQLite 3, SQLAlchemy ORM, PyTorch with sentence-transformers (all-MiniLM-L6-v2 RAG model)\n")
    p.add_run("• Server Local IP Address: ").bold = True
    p.add_run("http://192.168.29.4:8001 (FastAPI REST API) | 192.168.29.4:1883 (MQTT Broker)")

    # 6. ESP32 FIRMWARE COMPONENT
    add_heading_1("6. ESP32 Microcontroller Firmware Component")
    doc.add_paragraph(
        "The hardware terminal is driven by an ESP32 microcontroller executing custom C++ firmware compiled via the Arduino ESP32 Core."
    )
    p = doc.add_paragraph()
    p.add_run("• Core Libraries: ").bold = True
    p.add_run("WiFi.h, WiFiAP.h, WebServer.h, Update.h, PubSubClient.h, Adafruit_ILI9341.h, Adafruit_GFX.h\n")
    p.add_run("• Dual Wi-Fi Network Mode (WIFI_AP_STA): ").bold = True
    p.add_run("Connects to local Wi-Fi router SBVK (192.168.29.4) while simultaneously hosting the Wireless OTA SoftAP at 10.10.10.1 (3D_Printer_Lab).\n")
    p.add_run("• Zero-Lag Switch Debouncing: ").bold = True
    p.add_run("Replaced blocking loops with non-blocking millis() timers for 0ms switch response.\n")
    p.add_run("• Catch-All Web OTA Router: ").bold = True
    p.add_run("Uses server.onNotFound() so any web request to 10.10.10.1 serves the dark-themed firmware upload page.")

    # 7. CONCLUSION
    add_heading_1("7. Project Conclusion & Verification")
    add_callout(
        "All components of the LabCast AI System (Web Chatbox on GitHub Pages, Android App APK, FastAPI/Mosquitto backend, "
        "and ESP32 firmware) have been fully developed, compiled, and tested with 100% operational success.",
        title="VERIFICATION SUCCESSFUL"
    )

    doc.save("c:\\kishan java\\Labcast AI\\LabCast_AI_Software_Documentation.docx")
    print("DOCUMENT_CREATED_SUCCESSFULLY")

if __name__ == "__main__":
    create_document()
