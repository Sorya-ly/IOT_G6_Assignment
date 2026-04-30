import cv2
import paho.mqtt.client as mqtt
from ultralytics import YOLO
import json
import time
import urllib.request
import numpy as np
import threading

ESP32_IP    = "YOUR_IP"
ESP32_STREAM = f"http://{ESP32_IP}:81/stream"
ESP32_CAPTURE = f"http://{ESP32_IP}/capture"

MQTT_BROKER = "localhost"
MQTT_TOPIC  = "camera/detection"

YOLO_IMGSZ        = 320
YOLO_CONF         = 0.4
PUBLISH_INTERVAL  = 0.2
WINDOW_NAME       = "Person Detection"


class StreamGrabber:
    """Reads MJPEG via OpenCV's VideoCapture in a background thread,
    always exposing the latest frame."""

    def __init__(self, url):
        self.cap = cv2.VideoCapture(url)
        try:
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception:
            pass
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open stream {url}")
        self._frame = None
        self._lock = threading.Lock()
        self._running = True
        self._thread = threading.Thread(target=self._reader, daemon=True)
        self._thread.start()

    def _reader(self):
        while self._running:
            ok, frame = self.cap.read()
            if not ok:
                time.sleep(0.02)
                continue
            with self._lock:
                self._frame = frame

    def read(self):
        with self._lock:
            return None if self._frame is None else self._frame.copy()

    def stop(self):
        self._running = False
        self._thread.join(timeout=1)
        self.cap.release()


class CaptureGrabber:
    """Fallback: hits /capture in a background thread as fast as it can."""

    def __init__(self, url):
        self.url = url
        self._frame = None
        self._lock = threading.Lock()
        self._running = True
        self._thread = threading.Thread(target=self._reader, daemon=True)
        self._thread.start()

    def _reader(self):
        while self._running:
            try:
                resp = urllib.request.urlopen(self.url, timeout=5)
                buf = np.frombuffer(resp.read(), dtype=np.uint8)
                frame = cv2.imdecode(buf, cv2.IMREAD_COLOR)
                if frame is not None:
                    with self._lock:
                        self._frame = frame
            except Exception:
                time.sleep(0.1)

    def read(self):
        with self._lock:
            return None if self._frame is None else self._frame.copy()

    def stop(self):
        self._running = False
        self._thread.join(timeout=1)


def make_grabber():
    print(f"Trying MJPEG stream {ESP32_STREAM}...")
    try:
        return StreamGrabber(ESP32_STREAM)
    except Exception as e:
        print(f"Stream not available ({e}); falling back to /capture polling.")
        return CaptureGrabber(ESP32_CAPTURE)


def main():
    model = YOLO("1/best.pt")

    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    except AttributeError:
        client = mqtt.Client()

    try:
        client.connect(MQTT_BROKER, 1883, keepalive=60)
        client.loop_start()
    except Exception as e:
        print(f"MQTT connect failed ({MQTT_BROKER}:1883): {e}")
        raise SystemExit(1)

    grabber = make_grabber()

    for _ in range(50):
        if grabber.read() is not None:
            break
        time.sleep(0.1)
    else:
        print("No frames received within 5s — check the camera.")
        grabber.stop()
        raise SystemExit(1)

    print("Starting detection...")

    last_pub  = 0.0
    fps_t0    = time.time()
    fps_count = 0

    try:
        while True:
            frame = grabber.read()
            if frame is None:
                time.sleep(0.005)
                continue

            results    = model(frame, verbose=False,
                               imgsz=YOLO_IMGSZ, conf=YOLO_CONF)
            detections = results[0].boxes
            count      = len(detections)

            now = time.time()
            if now - last_pub >= PUBLISH_INTERVAL:
                payload = json.dumps({
                    "detected": count > 0,
                    "count":    count,
                    "timestamp": int(now),
                })
                client.publish(MQTT_TOPIC, payload)
                print(f"Published: {payload}")
                last_pub = now

            fps_count += 1
            if now - fps_t0 >= 2.0:
                fps = fps_count / (now - fps_t0)
                cv2.setWindowTitle(WINDOW_NAME, f"{WINDOW_NAME} — {fps:.1f} FPS") \
                    if hasattr(cv2, "setWindowTitle") else None
                fps_t0, fps_count = now, 0

            annotated = results[0].plot()
            cv2.imshow(WINDOW_NAME, annotated)
            if cv2.waitKey(1) == ord('q'):
                break
    finally:
        grabber.stop()
        cv2.destroyAllWindows()
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
