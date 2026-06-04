import os
import cv2
import mediapipe as mp
import numpy as np
import customtkinter as ctk
from PIL import Image, ImageTk

# Initialize MediaPipe Selfie Segmentation model
# Initialize MediaPipe Selfie Segmentation if available
try:
    mp_selfie_segmentation = mp.solutions.selfie_segmentation
    selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)
    HAS_MEDIAPIPE = True
except Exception:
    try:
        from mediapipe import solutions as _mp_solutions
        mp_selfie_segmentation = _mp_solutions.selfie_segmentation
        selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)
        HAS_MEDIAPIPE = True
    except Exception:
        selfie_segmentation = None
        HAS_MEDIAPIPE = False

# Base paths
BASE_DIR = os.path.dirname(__file__)
IMAGES_DIR = os.path.join(BASE_DIR, "images")

def safe_imread(path, flags=cv2.IMREAD_COLOR):
    if path is None:
        return None
    if not os.path.isabs(path):
        path = os.path.join(IMAGES_DIR, path)
    if os.path.exists(path):
        return cv2.imread(path, flags)
    return None

def load_bg(image_path):
    img = safe_imread(image_path, cv2.IMREAD_COLOR)
    if img is not None:
        return cv2.resize(img, (640, 480))
    return None

# Load Background Images (fall back to solid color if missing)
bg_image1 = load_bg('background.jpeg') or np.full((480, 640, 3), (40, 40, 60), dtype=np.uint8)
bg_image2 = load_bg('background2.jpeg') or np.full((480, 640, 3), (60, 40, 40), dtype=np.uint8)

# Load Face Cascade for Filter Application
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Load Filter Images from local `images/` folder
glasses1 = safe_imread('glasses.png', cv2.IMREAD_UNCHANGED)
glasses2 = safe_imread('glasses2.png', cv2.IMREAD_UNCHANGED)
glasses3 = safe_imread('glasses1.png', cv2.IMREAD_UNCHANGED)
mustache = safe_imread('mustache.png', cv2.IMREAD_UNCHANGED)
clown_nose = safe_imread('clown_nose.png', cv2.IMREAD_UNCHANGED)
party_hat = safe_imread('party_hat.png', cv2.IMREAD_UNCHANGED)

# Start Video Capture
cap = cv2.VideoCapture(0)

# Default mode
mode = 'original'
selected_filter = None  
show_age = False  # Toggle for age estimation

# Function to change mode (Blur, Background 1, Background 2)
def set_mode(new_mode):
    global mode
    mode = new_mode

# Function to change face filter
def set_filter(filter_name):
    global selected_filter
    selected_filter = filter_name

# Function to toggle age estimation
def toggle_age():
    global show_age
    show_age = not show_age

# Function to Blur Background
def blur_background(frame, mask):
    blurred_frame = cv2.GaussianBlur(frame, (55, 55), 0)
    mask_3channel = np.repeat(mask, 3, axis=-1)
    blended = (mask_3channel * frame + (1 - mask_3channel) * blurred_frame).astype(np.uint8)
    return blended

# Function to Replace Background
def replace_background(frame, mask, bg_image):
    bg_resized = cv2.resize(bg_image, (frame.shape[1], frame.shape[0]))
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    bg_resized_rgb = cv2.cvtColor(bg_resized, cv2.COLOR_BGR2RGB)
    blended = (mask * frame + (1 - mask) * bg_resized).astype(np.uint8)

    return blended.astype(np.uint8)

# Function to Apply Face Filters

def apply_filter(frame):
    global selected_filter

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    filtered_frame = frame.copy()

    for (x, y, w, h) in faces:
        filter_img = None
        fx, fy = x, y 

        if selected_filter == 'glasses1':
            filter_img = glasses1
            fx, fy = x, y + int(h * 0.25)
        elif selected_filter == 'glasses2':
            filter_img = glasses2
            fx, fy = x, y + int(h * 0.25)
        elif selected_filter == 'glasses3':
            filter_img = glasses3
            fx, fy = x, y + int(h * 0.25)
        elif selected_filter == 'mustache':
            filter_img = mustache
            mustache_width = int(w * 0.9)  # 60% of face width
            mustache_height = int(h * 0.7)  # 20% of face height
            fx = x + int(w * 0.1)  # Centering horizontally
            fy = y + int(h * 0.20)  # Placing it below nose
        elif selected_filter == 'clown_nose':
            filter_img = clown_nose
            nose_width = int(w * 0.7)  # 20% of face width
            nose_height = int(h * 0.80)  # 15% of face height
            fx = x + int(w * 0.2)  # Centering nose
            fy = y + int(h * 0.25)  # Placing it over nose
        elif selected_filter == 'party_hat':
            filter_img = party_hat
            fx, fy = x, y - int(h * 0.3)

        if filter_img is not None:
            # Resize filter based on face size
            try:
                if selected_filter == 'mustache':
                    resized_filter = cv2.resize(filter_img, (mustache_width, mustache_height))
                elif selected_filter == 'clown_nose':
                    resized_filter = cv2.resize(filter_img, (nose_width, nose_height))
                else:
                    # glasses and hats: base width on face width
                    resized_filter = cv2.resize(filter_img, (max(1, w), max(1, int(h / 3))))

                h_, w_ = resized_filter.shape[:2]
                if 0 <= fx < frame.shape[1] - w_ and 0 <= fy < frame.shape[0] - h_:
                    # handle alpha channel safely
                    if resized_filter.shape[2] == 4:
                        alpha = resized_filter[:, :, 3] / 255.0
                    else:
                        alpha = np.ones((h_, w_), dtype=np.float32)

                    for c in range(3):
                        fg = resized_filter[:, :, c]
                        bg = filtered_frame[fy:fy + h_, fx:fx + w_, c]
                        filtered_frame[fy:fy + h_, fx:fx + w_, c] = (
                            fg * alpha + bg * (1 - alpha)
                        ).astype(np.uint8)
            except Exception:
                # If resizing or blending fails for any reason, skip this filter
                pass



        # Show estimated age if enabled
        if show_age:
            if w < 100:
                age_group = "Child (0-12)"
            elif w < 150:
                age_group = "Teenager (13-19)"
            elif w < 200:
                age_group = "Adult (20-40)"
            else:
                age_group = "Senior (40+)"

            cv2.putText(filtered_frame, f"Age: {age_group}", (x, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    return filtered_frame
# Function to Process Video

def process_video():
    global mode
    ret, frame = cap.read()
    if not ret:
        root.after(10, process_video)
        return

    frame = cv2.resize(frame, (640, 480))
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    if selfie_segmentation is not None:
        result = selfie_segmentation.process(rgb_frame)
        mask = result.segmentation_mask if result is not None else None
    else:
        mask = None
    if mask is None:
        mask = np.ones((frame.shape[0], frame.shape[1]), dtype=np.uint8)
    mask = np.where(mask > 0.5, 1, 0).astype(np.uint8)
    mask_3d = np.repeat(mask[:, :, np.newaxis], 3, axis=2)

    if mode == 'blur':
        blurred_bg = cv2.GaussianBlur(frame, (55, 55), 0)
        output = (mask_3d * frame) + ((1 - mask_3d) * blurred_bg)
    elif mode == 'bg1' and bg_image1 is not None:
        output = (mask_3d * frame) + ((1 - mask_3d) * bg_image1)
    elif mode == 'bg2' and bg_image2 is not None:
        output = (mask_3d * frame) + ((1 - mask_3d) * bg_image2)
    else:
        output = frame

    # Apply Face Filters Here
    output = apply_filter(output)  # apply selected face filter

    output = output.astype(np.uint8)  
    img = Image.fromarray(cv2.cvtColor(output, cv2.COLOR_BGR2RGB))  
    imgtk = ImageTk.PhotoImage(image=img)
    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)

    # schedule next frame
    try:
        root.after(10, process_video)
    except Exception:
        pass


# Create GUI
ctk.set_appearance_mode("dark")
root = ctk.CTk()
root.title("Snapchat & Background Filter App")
root.geometry("900x650")

frame_container = ctk.CTkFrame(root)
frame_container.pack(pady=10, padx=10, fill="both", expand=True)

video_label = ctk.CTkLabel(frame_container, text="")
video_label.pack()

button_frame = ctk.CTkFrame(root)
button_frame.pack(pady=10)

# Background Buttons
# Background Selection Buttons
ctk.CTkButton(button_frame, text="Blur BG", command=lambda: set_mode('blur')).grid(row=0, column=0, padx=5, pady=5)
ctk.CTkButton(button_frame, text="BG 1", command=lambda: set_mode('bg1')).grid(row=0, column=1, padx=5, pady=5)
ctk.CTkButton(button_frame, text="BG 2", command=lambda: set_mode('bg2')).grid(row=0, column=2, padx=5, pady=5)

# First row - Glasses filters
btn_glasses1 = ctk.CTkButton(button_frame, text="Glasses 1", command=lambda: set_filter('glasses1'))
btn_glasses1.grid(row=1, column=0, padx=10, pady=5)

btn_glasses2 = ctk.CTkButton(button_frame, text="Glasses 2", command=lambda: set_filter('glasses2'))
btn_glasses2.grid(row=1, column=1, padx=10, pady=5)

btn_glasses3 = ctk.CTkButton(button_frame, text="Glasses 3", command=lambda: set_filter('glasses3'))
btn_glasses3.grid(row=1, column=2, padx=10, pady=5)

# Second row - Facial accessories
btn_mustache = ctk.CTkButton(button_frame, text="Mustache", command=lambda: set_filter('mustache'))
btn_mustache.grid(row=2, column=0, padx=10, pady=5)

btn_clown_nose = ctk.CTkButton(button_frame, text="Clown Nose", command=lambda: set_filter('clown_nose'))
btn_clown_nose.grid(row=2, column=1, padx=10, pady=5)

btn_party_hat = ctk.CTkButton(button_frame, text="Party Hat", command=lambda: set_filter('party_hat'))
btn_party_hat.grid(row=2, column=2, padx=10, pady=5)

# Third row - Additional Features


ctk.CTkButton(button_frame, text="Toggle Age", command=toggle_age).grid(row=3, column=0, padx=10, pady=5)

ctk.CTkButton(button_frame, text="Quit", command=root.destroy).grid(row=3, column=1, padx=10, pady=5)

# Add a button to clear filters
ctk.CTkButton(button_frame, text="No Filter", command=lambda: set_filter(None)).grid(row=3, column=2, padx=10, pady=5)

def cleanup():
    try:
        cap.release()
    except Exception:
        pass
    try:
        root.destroy()
    except Exception:
        pass

root.protocol("WM_DELETE_WINDOW", cleanup)

process_video()
root.mainloop()
