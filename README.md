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

## Run
Start the main app (webcam required):

```powershell
python snapchat.py
```

Run the face-swap demo (may be disabled if MediaPipe not available):

```powershell
python one.py
```

## Troubleshooting
- If you see errors like "module 'mediapipe' has no attribute 'solutions'":

```powershell
python -c "import mediapipe as mp; print('has_solutions=', hasattr(mp, 'solutions')); print(mp.__file__)"
```

Then reinstall MediaPipe:

```bash
pip install --upgrade mediapipe
```

On some Windows setups you may need a specific wheel or a newer Python version.

- If filters don't appear, ensure the correct image names live in `images/`.

## Notes
- The project includes fallbacks when MediaPipe segmentation/face-mesh aren't available; the app will still run with reduced features.
- If you want, I can add a `requirements.txt` and a short tutorial for capturing and inserting custom face images.
- 
