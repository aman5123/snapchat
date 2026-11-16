# Snapchat-style Filters (local)

Small desktop app demonstrating background replacement and face filters using OpenCV and MediaPipe.

## Requirements
- Python 3.8+
- pip packages:
  - opencv-python
  - mediapipe
  - numpy
  - customtkinter
  - Pillow

Install quickly:

```bash
python -m pip install --upgrade pip
pip install opencv-python mediapipe numpy customtkinter Pillow
```

## Files
- `snapchat.py`: Main GUI app (backgrounds, filters).
- `one.py`: Face-swap demo (requires example face images).
- `images/`: Put filter and background images here. Existing sample names:
  - glasses.png, glasses1.png, glasses2.png, mustache.png, clown_nose.png, party_hat.png
  - Optional: background.jpeg, background2.jpeg


