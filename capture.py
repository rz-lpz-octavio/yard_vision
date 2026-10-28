import os
import sys
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Transporte TCP para RTSP, mas estable que UDP
os.environ.setdefault("OPENCV_FFMPEG_CAPTURE_OPTIONS", "rtsp_transport;tcp")

import cv2

DVR_HOST = os.environ.get("DVR_HOST", "")
DVR_USER = os.environ.get("DVR_USER", "")
DVR_PASS = os.environ.get("DVR_PASS", "")
RTSP_URL = os.environ.get(
    "RTSP_URL",
    f"rtsp://{DVR_USER}:{DVR_PASS}@{DVR_HOST}:554/Streaming/Channels/101",
)
OUTPUT_DIR = "dataset/raw"
INTERVAL_SECONDS = 2.0
MAX_FRAMES = 0
JPEG_QUALITY = 90
RECONNECT_DELAY = 3.0


def open_stream(url):
    cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # buffer minimo, frames frescos
    return cap


def main():
    out = Path(OUTPUT_DIR)
    out.mkdir(parents=True, exist_ok=True)

    if not DVR_HOST and "RTSP_URL" not in os.environ:
        print("Falta DVR_HOST en .env (o RTSP_URL). Ver .env.example.")
        sys.exit(1)

    cap = open_stream(RTSP_URL)
    if not cap.isOpened():
        print("No se pudo abrir el stream. Verifica credenciales y red.")
        return

    saved = 0
    last_save = 0.0
    print("Capturando. Ctrl+C para detener.")
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                # stream caido, reconectar
                print("Lectura fallida, reconectando...")
                cap.release()
                time.sleep(RECONNECT_DELAY)
                cap = open_stream(RTSP_URL)
                continue

            now = time.monotonic()
            if now - last_save >= INTERVAL_SECONDS:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                path = out / f"frame_{ts}.jpg"
                cv2.imwrite(str(path), frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
                saved += 1
                last_save = now
                print(f"[{saved}] {path}")
                if MAX_FRAMES and saved >= MAX_FRAMES:
                    break
    except KeyboardInterrupt:
        print("\nDetenido por el usuario.")
    finally:
        cap.release()
    print(f"Total guardados: {saved}")


if __name__ == "__main__":
    main()
