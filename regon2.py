import tkinter as tk
from tkinter import messagebox
import cv2
import face_recognition
import numpy as np
import sqlite3
from PIL import Image, ImageTk
import pickle

# ========== Database Setup ==========
conn = sqlite3.connect("face_data.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    encoding BLOB NOT NULL
)
""")
conn.commit()


# ========== Functions ==========
def register_face(name, frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)

    if not face_locations:
        messagebox.showerror("Error", "No face detected. Try again.")
        return

    encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
    encoding_blob = pickle.dumps(encoding)
    cursor.execute("INSERT INTO users (name, encoding) VALUES (?, ?)", (name, encoding_blob))
    conn.commit()
    messagebox.showinfo("Success", f"Face registered for {name}.")


def recognize_face(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)

    if not face_locations:
        messagebox.showerror("Error", "No face detected.")
        return

    unknown_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
    cursor.execute("SELECT name, encoding FROM users")
    records = cursor.fetchall()

    for name, blob in records:
        known_encoding = pickle.loads(blob)
        result = face_recognition.compare_faces([known_encoding], unknown_encoding, tolerance=0.5)
        if result[0]:
            messagebox.showinfo("Match Found", f"Hello, {name}!")
            return

    messagebox.showwarning("No Match", "No match found.")


# ========== GUI Class ==========
class FaceRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition System")
        self.root.geometry("400x500")
        self.root.configure(bg="#f0f0f0")

        self.label = tk.Label(root, text="Face Recognition", font=("Helvetica", 16, "bold"), bg="#f0f0f0")
        self.label.pack(pady=10)

        self.video_label = tk.Label(root)
        self.video_label.pack()

        self.name_entry = tk.Entry(root, font=("Arial", 12))
        self.name_entry.pack(pady=10)
        self.name_entry.insert(0, "Enter Name")

        self.register_button = tk.Button(root, text="Register Face", command=self.register_user, bg="#4CAF50", fg="white", font=("Arial", 12))
        self.register_button.pack(pady=5)

        self.recognize_button = tk.Button(root, text="Recognize Face", command=self.recognize_user, bg="#2196F3", fg="white", font=("Arial", 12))
        self.recognize_button.pack(pady=5)

        self.quit_button = tk.Button(root, text="Exit", command=self.close_app, bg="#f44336", fg="white", font=("Arial", 12))
        self.quit_button.pack(pady=5)

        self.cap = cv2.VideoCapture(0)
        self.current_frame = None
        self.update_video()

    def update_video(self):
        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        self.root.after(10, self.update_video)

    def register_user(self):
        name = self.name_entry.get().strip()
        if not name or name == "Enter Name":
            messagebox.showerror("Error", "Please enter a valid name.")
            return
        register_face(name, self.current_frame)

    def recognize_user(self):
        recognize_face(self.current_frame)

    def close_app(self):
        self.cap.release()
        self.root.destroy()


# ========== Main ==========
if __name__ == "__main__":
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.mainloop()


