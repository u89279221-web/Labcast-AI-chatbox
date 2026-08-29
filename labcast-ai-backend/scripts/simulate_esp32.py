"""
ESP32 Hardware Simulator for LabCast AI
=======================================
Usage:
    python scripts/simulate_esp32.py --machine CNC01 --url http://127.0.0.1:8000 [--mqtt]

This script mimics the behavior of the ESP32 firmware running on the lab hardware.
It polls the configuration endpoint every 7 seconds and displays the
machine's SOP, safety guidelines, and emergency state exactly like a Serial Monitor.

If run with --mqtt, it will also connect to a local MQTT broker to subscribe to real-time
notifications (e.g., labcast/{machine_id}/emergency). This demonstrates the end-to-end 
pub/sub path, while REST polling remains a robust fallback mechanism for when 
messages are missed or the broker goes down.
"""

import time
import argparse
import requests
import sys
import json
import threading

# Global state for thread-safe access between MQTT and REST loop
current_state = {
    "is_emergency": False,
    "name": "",
    "sop": [],
    "safety_text": ""
}

def print_emergency_trigger():
    print("\n" + "!" * 50)
    print("!!! EMERGENCY ACTIVE (Triggered via MQTT) !!!")
    print("!!! INITIATING HARDWARE SHUTDOWN RELAYS !!!")
    print("!" * 50 + "\n")

def on_mqtt_message(client, userdata, msg):
    """Callback for when a PUBLISH message is received from the server."""
    try:
        payload = json.loads(msg.payload.decode())
        if msg.topic.endswith("/emergency"):
            new_emergency = payload.get("emergency", False)
            if new_emergency and not current_state["is_emergency"]:
                current_state["is_emergency"] = True
                print_emergency_trigger()
            elif not new_emergency and current_state["is_emergency"]:
                current_state["is_emergency"] = False
                print("\n[*] Emergency cleared via MQTT. Normal operation resumed.\n")
                
        elif msg.topic.endswith("/config"):
            current_state["name"] = payload.get("name", current_state["name"])
            current_state["sop"] = payload.get("sop", current_state["sop"])
            current_state["safety_text"] = payload.get("safety_text", current_state["safety_text"])
            print("\n[*] Configuration updated via MQTT in real-time.\n")
            
    except Exception as e:
        print(f"[!] MQTT Parse Error: {e}")

def setup_mqtt(machine_id: str, broker_host: str = "127.0.0.1", broker_port: int = 1883):
    import paho.mqtt.client as mqtt
    
    client = mqtt.Client(client_id=f"sim_esp32_{machine_id}")
    client.on_message = on_mqtt_message
    
    print(f"[*] Connecting to MQTT broker at {broker_host}:{broker_port}...")
    try:
        client.connect(broker_host, broker_port, 60)
        client.subscribe(f"labcast/{machine_id}/emergency")
        client.subscribe(f"labcast/{machine_id}/config")
        print("[*] MQTT Connected & Subscribed successfully.")
        
        # Start MQTT loop in background thread
        client.loop_start()
        return client
    except Exception as e:
        print(f"[!] MQTT Connection failed: {e}")
        return None

def simulate_hardware(machine_id: str, base_url: str, use_mqtt: bool):
    """
    Main loop that simulates the ESP32 hardware.
    """
    device_id = f"ESP32-{machine_id}"
    api_endpoint = f"{base_url.rstrip('/')}/api/machine/{machine_id}/config"
    register_endpoint = f"{base_url.rstrip('/')}/api/device/register"
    heartbeat_endpoint = f"{base_url.rstrip('/')}/api/device/{device_id}/heartbeat"
    
    print(f"[*] Booting simulated ESP32 for machine '{machine_id}'")
    print(f"[*] Registering device '{device_id}'...")
    
    try:
        reg_resp = requests.post(register_endpoint, json={
            "id": device_id,
            "machine_id": machine_id,
            "firmware_version": "v1.0.0-sim"
        }, timeout=5)
        reg_resp.raise_for_status()
        print("[*] Registration successful!")
    except requests.exceptions.RequestException as e:
        print(f"[!] WARNING: Failed to register device: {e}")

    mqtt_client = None
    if use_mqtt:
        mqtt_client = setup_mqtt(machine_id)

    print(f"[*] Polling REST endpoint: {api_endpoint} (every 7s)")
    print("-" * 60)

    was_emergency = False

    while True:
        try:
            # 1. Fetch current configuration from backend (Fallback / Reconciliation)
            response = requests.get(api_endpoint, timeout=5)
            
            if response.status_code == 404:
                print(f"[!] ERROR: Machine '{machine_id}' not found on backend.")
                time.sleep(7)
                continue
                
            response.raise_for_status()
            data = response.json()

            # 1.5 Send Heartbeat
            try:
                requests.post(heartbeat_endpoint, json={
                    "config_version": "1.0",
                    "wifi_signal": -65
                }, timeout=3)
            except requests.exceptions.RequestException:
                pass # Ignore heartbeat failures in loop to keep polling resilient

            # 2. Update global state from REST
            current_state["name"] = data.get("name", machine_id)
            current_state["sop"] = data.get("sop", [])
            current_state["safety_text"] = data.get("safety_text", "")
            
            # Reconcile emergency state
            rest_emergency = data.get("emergency", False)
            if rest_emergency and not current_state["is_emergency"]:
                current_state["is_emergency"] = True
                print("\n" + "!" * 50)
                print("!!! EMERGENCY ACTIVE (Triggered via REST Polling Fallback) !!!")
                print("!!! INITIATING HARDWARE SHUTDOWN RELAYS !!!")
                print("!" * 50 + "\n")
            elif not rest_emergency and current_state["is_emergency"]:
                current_state["is_emergency"] = False
                print("\n[*] Emergency cleared via REST Polling. Normal operation resumed.\n")

            was_emergency = current_state["is_emergency"]

            # 3. Normal Serial Monitor Output
            print(f"[{time.strftime('%H:%M:%S')}] {current_state['name']} (ID: {machine_id})")
            print(f"   Emergency Status: {'ACTIVE' if was_emergency else 'Clear'}")
            print(f"   Safety Config: {current_state['safety_text']}")
            print(f"   SOP Steps ({len(current_state['sop'])}):")
            for i, step in enumerate(current_state['sop'], 1):
                print(f"     {i}. {step}")
            print("-" * 60)

        except requests.exceptions.RequestException as e:
            print(f"[{time.strftime('%H:%M:%S')}] [!] REST Connection failed: {e}")

        # Sleep to mimic ESP32 polling delay (7 seconds)
        time.sleep(7)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate ESP32 hardware for a LabCast machine.")
    parser.add_argument(
        "--machine", 
        type=str, 
        required=True, 
        help="The Machine ID to simulate (e.g., CNC01, LATHE02)"
    )
    parser.add_argument(
        "--url", 
        type=str, 
        default="http://127.0.0.1:8000",
        help="The base URL of the backend API (default: http://127.0.0.1:8000)"
    )
    parser.add_argument(
        "--mqtt", 
        action="store_true",
        help="Enable MQTT subscription mode for real-time pub/sub"
    )
    
    args = parser.parse_args()

    try:
        simulate_hardware(args.machine, args.url, args.mqtt)
    except KeyboardInterrupt:
        print("\n[*] Simulator manually stopped by user.")
        sys.exit(0)
