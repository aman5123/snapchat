import os
import cv2
import mediapipe as mp
import numpy as np
import customtkinter as ctk
from PIL import Image, ImageTk

class FaceSwapApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Live Face Swap")
        self.root.geometry("900x700")

        ctk.set_appearance_mode("dark")

        # Video Label
        self.video_label = ctk.CTkLabel(root)
        self.video_label.pack(pady=10)

        # Button Frame
        self.button_frame = ctk.CTkFrame(root)
        self.button_frame.pack(pady=10)

        self.swap_button1 = ctk.CTkButton(self.button_frame, text="Face 1", command=lambda: self.set_face("face1"))
        self.swap_button1.grid(row=0, column=0, padx=5)

        self.swap_button2 = ctk.CTkButton(self.button_frame, text="Face 2", command=lambda: self.set_face("face2"))
        self.swap_button2.grid(row=0, column=1, padx=5)

        self.swap_button3 = ctk.CTkButton(self.button_frame, text="Face 3", command=lambda: self.set_face("face3"))
        self.swap_button3.grid(row=0, column=2, padx=5)

        self.normal_button = ctk.CTkButton(root, text="Normal", command=self.set_normal)
        self.normal_button.pack(pady=5)

        self.quit_button = ctk.CTkButton(root, text="Quit", command=self.quit_app)
        self.quit_button.pack(pady=10)

        # Initialize variables
        self.mode = "normal"
        self.cap = cv2.VideoCapture(0)

        if not self.cap.isOpened():
            print("Error: Could not open webcam.")
            return

        # Initialize MediaPipe Face Mesh if available
        try:
            self.face_mesh = mp.solutions.face_mesh.FaceMesh(
                static_image_mode=False, max_num_faces=1, refine_landmarks=True)
        except Exception:
            try:
                from mediapipe import solutions as _mp_solutions
                self.face_mesh = _mp_solutions.face_mesh.FaceMesh(
                    static_image_mode=False, max_num_faces=1, refine_landmarks=True)
            except Exception:
                self.face_mesh = None
                print("Warning: MediaPipe Face Mesh not available. Face swap disabled.")

        # Load multiple celebrity images from local images folder (if present)
        base_dir = os.path.dirname(__file__)
        images_dir = os.path.join(base_dir, "images")
        self.faces = {
            "face1": cv2.imread(os.path.join(images_dir, "celebrity_face.jpeg")),
            "face2": cv2.imread(os.path.join(images_dir, "celebrity_face2.jpeg")),
            "face3": cv2.imread(os.path.join(images_dir, "user_face.jpeg")),
        }
        self.celebrity_landmarks = {}

        # Detect landmarks for all faces
        for key, img in self.faces.items():
            if img is not None:
                self.celebrity_landmarks[key] = self.detect_face_landmarks(img)
            else:
                print(f"Error: {key} image not found.")

        self.selected_face = None
        self.update_video()

    def set_face(self, face_key):
        if face_key in self.celebrity_landmarks and self.celebrity_landmarks[face_key] is not None:
            self.selected_face = face_key
            self.mode = "swap"
            print(f"Face swap activated with {face_key}!")
        else:
            print(f"Error: No landmarks detected for {face_key}. Face swap won't work.")
            self.mode = "normal"

    def set_normal(self):
        self.mode = "normal"

    def quit_app(self):
        self.cap.release()
        cv2.destroyAllWindows()
        self.root.quit()

    def detect_face_landmarks(self, image):
        if self.face_mesh is None:
            return None
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_image)
        if results and results.multi_face_landmarks:
            return np.array([[lm.x * image.shape[1], lm.y * image.shape[0]]
                             for lm in results.multi_face_landmarks[0].landmark])
        return None

    def apply_face_swap(self, frame):
        if not self.selected_face or self.celebrity_landmarks.get(self.selected_face) is None:
            print("No celebrity face detected!")
            return frame  

        source_landmarks = self.detect_face_landmarks(frame)
        if source_landmarks is None:
            print("No face detected in the webcam feed!")
            return frame  

        celeb_landmarks = self.celebrity_landmarks[self.selected_face]

        if len(celeb_landmarks) < 468 or len(source_landmarks) < 468:
            print(f"Insufficient landmarks detected. Found {len(source_landmarks)}")
            return frame  

        try:
            # Perform face swap
            src_pts = np.array(source_landmarks, dtype=np.int32)
            celeb_pts = np.array(celeb_landmarks, dtype=np.int32)

            # Convex Hull Matching
            hull_indices = cv2.convexHull(src_pts, returnPoints=False)
            src_hull = [src_pts[i[0]] for i in hull_indices]
            celeb_hull = [celeb_pts[i[0]] for i in hull_indices]

            rect = cv2.boundingRect(np.array(src_hull, dtype=np.int32))
            subdiv = cv2.Subdiv2D(rect)

            for p in src_hull:
                p = tuple(map(int, p))
                subdiv.insert(p)

            triangle_list = subdiv.getTriangleList()
            triangle_indices = []

            for t in triangle_list:
                pt1, pt2, pt3 = (t[:2], t[2:4], t[4:6])
                try:
                    idx1, idx2, idx3 = (src_pts.tolist().index(list(pt1)),
                                        src_pts.tolist().index(list(pt2)),
                                        src_pts.tolist().index(list(pt3)))
                    triangle_indices.append((idx1, idx2, idx3))
                except ValueError:
                    continue

            warped_celeb = np.zeros_like(frame, dtype=np.uint8)

            for t in triangle_indices:
                t1_src = np.float32([celeb_pts[t[0]], celeb_pts[t[1]], celeb_pts[t[2]]])
                t2_dest = np.float32([src_pts[t[0]], src_pts[t[1]], src_pts[t[2]]])

                warp_mat = cv2.getAffineTransform(t1_src, t2_dest)
                warped_tri = cv2.warpAffine(self.faces[self.selected_face], warp_mat, (frame.shape[1], frame.shape[0]))

                mask = np.zeros_like(frame[:, :, 0])
                cv2.fillConvexPoly(mask, np.int32(t2_dest), 255)

                warped_celeb = cv2.bitwise_and(warped_celeb, warped_celeb, mask=cv2.bitwise_not(mask))
                warped_celeb += cv2.bitwise_and(warped_tri, warped_tri, mask=mask)

            mask = np.zeros_like(frame[:, :, 0])
            cv2.fillConvexPoly(mask, np.int32(src_hull), 255)
            center = tuple(np.mean(src_hull, axis=0).astype(np.int32))
            swapped = cv2.seamlessClone(warped_celeb, frame, mask, center, cv2.NORMAL_CLONE)

            return swapped
        except Exception as e:
            print(f"Error in face swap: {e}")
            return frame

    def update_video(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            if self.mode == "swap":
                frame = self.apply_face_swap(frame)
            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        self.root.after(10, self.update_video)

if __name__ == "__main__":
    root = ctk.CTk()
    app = FaceSwapApp(root)
    root.mainloop()

