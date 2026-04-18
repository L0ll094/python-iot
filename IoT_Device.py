from abc import ABC, abstractmethod
from typing import Optional, Callable, Any
from dataclasses import dataclass
import time  # Replace asyncio with time
import paho.mqtt.client as mqtt
import json
import ssl
from datetime import datetime, timezone
## This program is run inside a private environment, you get the terminal to enter that
# by running: .\.venv\Scripts\Activate.ps1

# ============================================================================
# Data Classes for Type Safety
# ============================================================================

@dataclass
class MQTTConfig:
    """Configuration for MQTT connection"""
    broker_address: str
    broker_port: int = 1883
    username: Optional[str] = None
    password: Optional[str] = None
    client_id: Optional[str] = None
    
    # X.509 Certificate authentication (optional)
    ca_cert_path: Optional[str] = None      # CA certificate file path
    client_cert_path: Optional[str] = None  # Device certificate file path  
    private_key_path: Optional[str] = None  # Device private key file path


@dataclass
class DeviceMessage:
    """Structured message from a device"""
    device_id: str
    topic: str
    payload: dict[str, Any]
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def to_json(self) -> str:
        """Convert message to JSON"""
        return json.dumps({
            "device_id": self.device_id,
            "topic": self.topic,
            "payload": self.payload,
            "timestamp": self.timestamp
        })


# ============================================================================
# Abstract Base Device Class
# ============================================================================

class IoTDevice(ABC):
    """Base class for all IoT devices"""
    
    def __init__(
        self,
        device_id: str,
        mqtt_config: MQTTConfig,
        serial_number: float,
        on_connect: Optional[Callable] = None,
        on_disconnect: Optional[Callable] = None
        
    ):
        self.device_id = device_id
        self.mqtt_config = mqtt_config
        self.serial_number = 111
        self.client = mqtt.Client(client_id=device_id)
        self.is_connected = False
        
        # Set callbacks
        self.on_connect_callback = on_connect
        self.on_disconnect_callback = on_disconnect
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
    
    def _on_connect(self, client: mqtt.Client, userdata: Any, connect_flags: Any, reason_code: Any, properties: Any) -> None:
        """Internal callback when MQTT connects"""
        self.is_connected = True
        print(f"[{self.device_id}] Connected to MQTT broker")
        if self.on_connect_callback:
            self.on_connect_callback(self)
    
    def _on_disconnect(self, client: mqtt.Client, userdata: Any, disconnect_flags: Any, reason_code: Any, properties: Any) -> None:
        """Internal callback when MQTT disconnects"""
        self.is_connected = False
        print(f"[{self.device_id}] Disconnected from MQTT broker")
        if self.on_disconnect_callback:
            self.on_disconnect_callback(self)
    
    def _on_message(self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage) -> None:
        """Internal callback for incoming messages"""
        self.on_message(msg.topic, msg.payload.decode())
    
    def connect(self) -> None:
        """Connect to MQTT broker"""
        
        # Set up TLS with X.509 certificates if provided
        if self.mqtt_config.ca_cert_path and self.mqtt_config.client_cert_path and self.mqtt_config.private_key_path:
            self.client.tls_set(
                ca_certs=self.mqtt_config.ca_cert_path,
                certfile=self.mqtt_config.client_cert_path,
                keyfile=self.mqtt_config.private_key_path,
                tls_version=ssl.PROTOCOL_TLSv1_2
            )
            # Use secure MQTT port if not specified
            port = self.mqtt_config.broker_port if self.mqtt_config.broker_port != 1883 else 8883
        else:
            # Use username/password if no certificates
            if self.mqtt_config.username and self.mqtt_config.password:
                self.client.username_pw_set(
                    self.mqtt_config.username,
                    self.mqtt_config.password
                )
            port = self.mqtt_config.broker_port
        

        "Abstraction of connect-to-MQTT-method to include error handling"
        try: 
            self.client.connect(
                self.mqtt_config.broker_address,
                self.mqtt_config.broker_port,
                keepalive=60
            )
            print(f"[{self.device_id}] Successfully connected to MQTT broker")
            
        except Exception as e:
            print(f"[{self.device_id}] Error: Failed to connect to MQTT broker at {self.mqtt_config.broker_address}:{self.mqtt_config.broker_port}")
            self.is_connected = False

                
    
    def disconnect(self) -> None:
        """Disconnect from MQTT broker"""
        self.client.disconnect()
    
    def publish(self, message: DeviceMessage, qos: int = 1) -> None:
        """Publish a message to MQTT broker"""
        if not self.is_connected:
            print(f"[{self.device_id}] Warning: Not connected, queueing message")
        
        self.client.publish(
            message.topic,
            message.to_json(),
            qos=qos
        )
    
    def subscribe(self, topic: str, qos: int = 1) -> None:
        """Subscribe to a topic"""
        self.client.subscribe(topic, qos=qos)
    
    # ========================================================================
    # Abstract Methods - Subclasses Must Implement These
    # ========================================================================
    
    @abstractmethod
    def run(self) -> None:
        """Main device logic - what the device should do"""
        pass
    
    @abstractmethod
    def on_message(self, topic: str, payload: str) -> None:
        """Handle incoming messages from subscribed topics"""
        pass


# ============================================================================
# Example Concrete Device Implementation
# ============================================================================

class TemperatureSensor(IoTDevice):
    """Example: A temperature sensor device"""
    
    def __init__(self, device_id: str, mqtt_config: MQTTConfig):
        super().__init__(device_id, mqtt_config, serial_number=111)
        self.temperature = 20.0
    
    def run(self) -> None:
        """Simulate temperature readings and publish them"""
        self.connect()
        
        try:
            for i in range(10):
                # Simulate temperature change
                self.temperature += (i % 2) * 0.5 - 0.25  # Random-ish variation
                
                # Create and publish message
                message = DeviceMessage(
                    device_id=self.device_id,
                    topic=f"devices/{self.device_id}/temperature",
                    payload={"temp_celsius": round(self.temperature, 2), "unit": "C"}
                )
                
                self.publish(message)
                print(f"[{self.device_id}] Published: {self.temperature:.2f}°C")
                
                # Wait before next reading
                time.sleep(2)
        
        finally:
            self.disconnect()
    
    def on_message(self, topic: str, payload: str) -> None:
        """Handle incoming commands"""
        print(f"[{self.device_id}] Received message on {topic}: {payload}")


# ============================================================================
# Example Usage
# ============================================================================

def main():
    """Example of running a single device"""
    
    # Configure MQTT broker with X.509 certificates
    mqtt_config = MQTTConfig(
        broker_address="a1ax2c7i1tgioq-ats.iot.eu-north-1.amazonaws.com", 
        broker_port=8883,
        ca_cert_path="C:/Users/louis/Documents/Code Repos/python_iot/cert/AmazonRootCA1.pem",
        client_cert_path="C:/Users/louis/Documents/Code Repos/python_iot/cert/0639a98033ec9fe3da771503029802a67fa5a5ddac16ed6670898810dd8f3087-certificate.pem.crt",
        private_key_path="C:/Users/louis/Documents/Code Repos/python_iot/cert/50104f8772ab8ac1b4173fddf543fc32b015fc38ea6dffed344c1ba857443b00-private.pem.key"
    )
    
    # Create and run a single temperature sensor
    sensor = TemperatureSensor("sensor_001", mqtt_config)
    sensor.run()


if __name__ == "__main__":
    # Run the example
    main()
