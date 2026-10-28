# yard_vision

RTSP frame grabber for a HiLook DVR. Grabs frames on an interval for building an object-detection dataset.

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env  # set your DVR credentials
python capture.py     # Ctrl+C to stop
```

Config goes in `.env`. See `.env.example` for the keys. Dataset and credentials are not in the repo.
