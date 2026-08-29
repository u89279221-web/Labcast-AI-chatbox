import json
import logging
import paho.mqtt.publish as publish
from app.core.config import settings

logger = logging.getLogger(__name__)

def publish_message(topic: str, payload: dict) -> None:
    """
    Publish a JSON payload to an MQTT topic.
    Fails silently (with a log warning) if the broker is unreachable or unconfigured,
    so that the REST API remains the robust source of truth.
    """
    if not settings.mqtt_broker_host:
        logger.debug(f"Skipping MQTT publish for topic '{topic}' - broker not configured.")
        return
        
    try:
        auth = None
        if settings.mqtt_username:
            auth = {
                'username': settings.mqtt_username, 
                'password': settings.mqtt_password or ''
            }
            
        publish.single(
            topic,
            payload=json.dumps(payload),
            hostname=settings.mqtt_broker_host,
            port=settings.mqtt_broker_port,
            auth=auth,
            client_id="labcast_backend_publisher"
        )
        logger.debug(f"Published MQTT message to '{topic}'")
    except Exception as e:
        logger.warning(f"Failed to publish MQTT message to '{topic}': {e}")
