# import cv2
# import mediapipe as mp
# import numpy as np
# import customtkinter as ctk
# from PIL import Image, ImageTk

# # Initialize MediaPipe Selfie Segmentation model
# mp_selfie_segmentation = mp.solutions.selfie_segmentation
# selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)

# face_mesh = mp.solutions.face_mesh.FaceMesh(
# static_image_mode=False, max_num_faces=1, refine_landmarks=True)
# def load_bg(image_path):
#     img = cv2.imread(image_path)
#     if img is not None:
#         return cv2.resize(img, (640, 480))
#     return None

# # Load Background Images
# bg_image1 = load_bg('background.jpeg')
# bg_image2 = load_bg('background2.jpeg')

# # Load Face Cascade for Filter Application
# face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# # Load Filter Images
# glasses1 = cv2.imread("C:/Users/akshita bhardwaj/OneDrive/Desktop/snapchat/images/glasses.png", cv2.IMREAD_UNCHANGED)
# glasses2 = cv2.imread("C:/Users/akshita bhardwaj/OneDrive/Desktop/snapchat/images/glasses2.png", cv2.IMREAD_UNCHANGED)
# glasses3 = cv2.imread("C:/Users/akshita bhardwaj/OneDrive/Desktop/snapchat/images/glasses1.png", cv2.IMREAD_UNCHANGED)
# mustache = cv2.imread("C:/Users/akshita bhardwaj/OneDrive/Desktop/snapchat/images/mustache.png", cv2.IMREAD_UNCHANGED)
# clown_nose = cv2.imread("C:/Users/akshita bhardwaj/OneDrive/Desktop/snapchat/images/clown_nose.png", cv2.IMREAD_UNCHANGED)
# party_hat = cv2.imread("C:/Users/akshita bhardwaj/OneDrive/Desktop/snapchat/images/party_hat.png", cv2.IMREAD_UNCHANGED)

# faces = {
#     "face1": cv2.imread("celebrity_face.jpeg"),
#     "face2": cv2.imread("celebrity_face2.jpeg"),
#     "face3": cv2.imread("user_face.jpeg"),
# }

# def detect_face_landmarks(image):
#     rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#     results = face_mesh.process(rgb_image)
#     if results.multi_face_landmarks:
#         return np.array([[lm.x * image.shape[1], lm.y * image.shape[0]] 
#                          for lm in results.multi_face_landmarks[0].landmark])
#     return None

# celebrity_landmarks = {}
# for key, img in faces.items():
#     if img is not None:
#         celebrity_landmarks[key] = detect_face_landmarks(img)
#     else:
#         print(f"Error: {key} image not found.")

# selected_face = None

# def apply_face_swap(frame):
#     if not selected_face or celebrity_landmarks.get(selected_face) is None:
#         print("No celebrity face detected!")
#         return frame  

#     source_landmarks = detect_face_landmarks(frame)
#     if source_landmarks is None:
#         print("No face detected in the webcam feed!")
#         return frame  

#     celeb_landmarks = celebrity_landmarks[selected_face]
#     if len(celeb_landmarks) < 468 or len(source_landmarks) < 468:
#         print(f"Insufficient landmarks detected. Found {len(source_landmarks)}")
#         return frame  

#     try:
#         src_pts = np.array(source_landmarks, dtype=np.int32)
#         celeb_pts = np.array(celeb_landmarks, dtype=np.int32)
        
#         hull_indices = cv2.convexHull(src_pts, returnPoints=False)
#         src_hull = [src_pts[i[0]] for i in hull_indices]
#         celeb_hull = [celeb_pts[i[0]] for i in hull_indices]

#         mask = np.zeros_like(frame[:, :, 0])
#         cv2.fillConvexPoly(mask, np.int32(src_hull), 255)
#         center = tuple(np.mean(src_hull, axis=0).astype(np.int32))
#         swapped = cv2.seamlessClone(faces[selected_face], frame, mask, center, cv2.NORMAL_CLONE)
#         return swapped
#     except Exception as e:
#         print(f"Error in face swap: {e}")
#         return frame

# def update_video():
#     ret, frame = cap.read()
#     if ret:
#         frame = cv2.flip(frame, 1)
#         if mode == "swap":
#             frame = apply_face_swap(frame)
#         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         img = Image.fromarray(frame)
#         imgtk = ImageTk.PhotoImage(image=img)
#         video_label.imgtk = imgtk
#         video_label.configure(image=imgtk)
#     root.after(10, update_video)

# cap = cv2.VideoCapture(0)
# if not cap.isOpened():
#     print("Error: Could not open webcam.")
# else:
#     update_video()

# # Default mode
# mode = 'original'
# selected_filter = None  
# show_age = False


# # Function to change mode (Blur, Background 1, Background 2)
# def set_mode(new_mode):
#     global mode
#     mode = new_mode

# # Function to change face filter
# def set_filter(filter_name):
#     global selected_filter
#     selected_filter = filter_name

# # Function to toggle age estimation
# def toggle_age():
#     global show_age
#     show_age = not show_age

# # Function to Blur Background
# def blur_background(frame, mask):
#     blurred_frame = cv2.GaussianBlur(frame, (55, 55), 0)
#     mask_3channel = np.repeat(mask, 3, axis=-1)
#     blended = (mask_3channel * frame + (1 - mask_3channel) * blurred_frame).astype(np.uint8)
#     return blended

# # Function to Replace Background
# def replace_background(frame, mask, bg_image):
#     bg_resized = cv2.resize(bg_image, (frame.shape[1], frame.shape[0]))
#     frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     bg_resized_rgb = cv2.cvtColor(bg_resized, cv2.COLOR_BGR2RGB)
#     blended = (mask * frame + (1 - mask) * bg_resized).astype(np.uint8)

#     return blended.astype(np.uint8)

# # Function to Apply Face Filters

# def apply_filter(frame):
#     global selected_filter

#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     faces = face_cascade.detectMultiScale(gray, 1.3, 5)

#     filtered_frame = frame.copy()

#     for (x, y, w, h) in faces:
#         filter_img = None
#         fx, fy = x, y 

#         if selected_filter == 'glasses1':
#             filter_img = glasses1
#             fx, fy = x, y + int(h * 0.25)
#         elif selected_filter == 'glasses2':
#             filter_img = glasses2
#             fx, fy = x, y + int(h * 0.25)
#         elif selected_filter == 'glasses3':
#             filter_img = glasses3
#             fx, fy = x, y + int(h * 0.25)
#         elif selected_filter == 'mustache':
#             filter_img = mustache
#             mustache_width = int(w * 0.9)  # 60% of face width
#             mustache_height = int(h * 0.7)  # 20% of face height
#             fx = x + int(w * 0.1)  # Centering horizontally
#             fy = y + int(h * 0.20)  # Placing it below nose
#         elif selected_filter == 'clown_nose':
#             filter_img = clown_nose
#             nose_width = int(w * 0.7)  # 20% of face width
#             nose_height = int(h * 0.80)  # 15% of face height
#             fx = x + int(w * 0.2)  # Centering nose
#             fy = y + int(h * 0.25)  # Placing it over nose
#         elif selected_filter == 'party_hat':
#             filter_img = party_hat
#             fx, fy = x, y - int(h * 0.3)

#         if filter_img is not None:
#             # Resize filter based on face size
#             if selected_filter == 'mustache':
#                 resized_filter = cv2.resize(filter_img, (mustache_width, mustache_height))
#             elif selected_filter == 'clown_nose':
#                 resized_filter = cv2.resize(filter_img, (nose_width, nose_height))
#             else:
#                 resized_filter = cv2.resize(filter_img, (w, int(h / 3)))

#             h_, w_ = resized_filter.shape[:2]
#             if 0 <= fx < frame.shape[1] - w_ and 0 <= fy < frame.shape[0] - h_:
#                 # for c in range(3):
#                    alpha = resized_filter[:, :, 3] / 255.0
#                    for c in range(3):  
#                         filtered_frame[fy:fy + h_, fx:fx + w_, c] = (
#                             resized_filter[:, :, c] * alpha +
#                             filtered_frame[fy:fy + h_, fx:fx + w_, c] * (1 - alpha)
#                         )



#         # Show estimated age if enabled
#         if show_age:
#             if w < 100:
#                 age_group = "Child (0-12)"
#             elif w < 150:
#                 age_group = "Teenager (13-19)"
#             elif w < 200:
#                 age_group = "Adult (20-40)"
#             else:
#                 age_group = "Senior (40+)"

#             cv2.putText(filtered_frame, f"Age: {age_group}", (x, y - 10), 
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

#     return filtered_frame
# # Function to Process Video

# def process_video():
#     global mode
#     ret, frame = cap.read()
#     if not ret:
#         root.after(10, process_video)
#         return

#     frame = cv2.resize(frame, (640, 480))  
#     rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  
#     result = selfie_segmentation.process(rgb_frame)
    
#     mask = result.segmentation_mask
#     mask = np.where(mask > 0.5, 1, 0).astype(np.uint8)  
#     mask_3d = np.repeat(mask[:, :, np.newaxis], 3, axis=2)  

#     if mode == 'blur':
#         blurred_bg = cv2.GaussianBlur(frame, (55, 55), 0)
#         output = (mask_3d * frame) + ((1 - mask_3d) * blurred_bg)
#     elif mode == 'bg1' and bg_image1 is not None:
#         output = (mask_3d * frame) + ((1 - mask_3d) * bg_image1)
#     elif mode == 'bg2' and bg_image2 is not None:
#         output = (mask_3d * frame) + ((1 - mask_3d) * bg_image2)
#     else:
#         output = frame  

#     # Apply Face Filters Here
#     output = apply_filter(output)  # Fix: Apply selected face filter

#     output = output.astype(np.uint8)  
#     img = Image.fromarray(cv2.cvtColor(output, cv2.COLOR_BGR2RGB))  
#     imgtk = ImageTk.PhotoImage(image=img)
#     video_label.imgtk = imgtk
#     video_label.configure(image=imgtk)

#     root.after(10, process_video)


# # Create GUI
# ctk.set_appearance_mode("dark")
# root = ctk.CTk()
# root.title("Snapchat & Background Filter App")
# root.geometry("900x650")

# frame_container = ctk.CTkFrame(root)
# frame_container.pack(pady=10, padx=10, fill="both", expand=True)

# video_label = ctk.CTkLabel(frame_container, text="")
# video_label.pack()

# button_frame = ctk.CTkFrame(root)
# button_frame.pack(pady=10)

# # Background Buttons
# # Background Selection Buttons
# ctk.CTkButton(button_frame, text="Blur BG", command=lambda: set_mode('blur')).grid(row=0, column=0, padx=5, pady=5)
# ctk.CTkButton(button_frame, text="BG 1", command=lambda: set_mode('bg1')).grid(row=0, column=1, padx=5, pady=5)
# ctk.CTkButton(button_frame, text="BG 2", command=lambda: set_mode('bg2')).grid(row=0, column=2, padx=5, pady=5)

# # First row - Glasses filters
# btn_glasses1 = ctk.CTkButton(button_frame, text="Glasses 1", command=lambda: set_filter('glasses1'))
# btn_glasses1.grid(row=1, column=0, padx=10, pady=5)

# btn_glasses2 = ctk.CTkButton(button_frame, text="Glasses 2", command=lambda: set_filter('glasses2'))
# btn_glasses2.grid(row=1, column=1, padx=10, pady=5)

# btn_glasses3 = ctk.CTkButton(button_frame, text="Glasses 3", command=lambda: set_filter('glasses3'))
# btn_glasses3.grid(row=1, column=2, padx=10, pady=5)

# # Second row - Facial accessories
# btn_mustache = ctk.CTkButton(button_frame, text="Mustache", command=lambda: set_filter('mustache'))
# btn_mustache.grid(row=2, column=0, padx=10, pady=5)

# btn_clown_nose = ctk.CTkButton(button_frame, text="Clown Nose", command=lambda: set_filter('clown_nose'))
# btn_clown_nose.grid(row=2, column=1, padx=10, pady=5)

# btn_party_hat = ctk.CTkButton(button_frame, text="Party Hat", command=lambda: set_filter('party_hat'))
# btn_party_hat.grid(row=2, column=2, padx=10, pady=5)

# # Third row - Additional Features


# ctk.CTkButton(button_frame, text="Toggle Age", command=toggle_age).grid(row=3, column=0, padx=10, pady=5)

# ctk.CTkButton(button_frame, text="Quit", command=root.destroy).grid(row=3, column=1, padx=10, pady=5)


# process_video()
# root.mainloop()


