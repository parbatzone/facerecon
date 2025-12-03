import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import face_recognition
import os
import threading

class FaceRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition Matcher")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f4f8")
        
        self.reference_image_path = None
        self.reference_encoding = None
        self.folder_path = None
        self.matches = []
        
        self.create_widgets()
    
    def create_widgets(self):
        # Title
        title_frame = tk.Frame(self.root, bg="#4f46e5", pady=15)
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            title_frame,
            text="👤 Face Recognition Matcher",
            font=("Arial", 24, "bold"),
            bg="#4f46e5",
            fg="white"
        )
        title_label.pack()
        
        # Main container
        main_frame = tk.Frame(self.root, bg="#f0f4f8", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Image upload
        left_frame = tk.LabelFrame(
            main_frame,
            text="📤 Upload Reference Image",
            font=("Arial", 12, "bold"),
            bg="white",
            padx=15,
            pady=15
        )
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.image_label = tk.Label(
            left_frame,
            text="No image selected\n\nClick 'Browse' to select an image",
            bg="white",
            fg="#6b7280",
            width=30,
            height=15,
            relief=tk.RIDGE,
            bd=2
        )
        self.image_label.pack(pady=10)
        
        browse_btn = tk.Button(
            left_frame,
            text="Browse Image",
            command=self.browse_image,
            bg="#4f46e5",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=10,
            cursor="hand2"
        )
        browse_btn.pack(pady=5)
        
        # Right side - Folder selection and search
        right_frame = tk.LabelFrame(
            main_frame,
            text="📁 Search Folder",
            font=("Arial", 12, "bold"),
            bg="white",
            padx=15,
            pady=15
        )
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        tk.Label(
            right_frame,
            text="Select folder to search:",
            font=("Arial", 10),
            bg="white"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        folder_input_frame = tk.Frame(right_frame, bg="white")
        folder_input_frame.pack(fill=tk.X, pady=5)
        
        self.folder_entry = tk.Entry(
            folder_input_frame,
            font=("Arial", 10),
            width=30
        )
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        folder_btn = tk.Button(
            folder_input_frame,
            text="Browse",
            command=self.browse_folder,
            bg="#6366f1",
            fg="white",
            font=("Arial", 9, "bold"),
            padx=10,
            cursor="hand2"
        )
        folder_btn.pack(side=tk.LEFT)
        
        # Search button
        self.search_btn = tk.Button(
            right_frame,
            text="🔍 Search for Matches",
            command=self.search_faces,
            bg="#10b981",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=30,
            pady=15,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.search_btn.pack(pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            right_frame,
            mode='indeterminate',
            length=300
        )
        self.progress.pack(pady=10)
        
        # Status label
        self.status_label = tk.Label(
            right_frame,
            text="",
            font=("Arial", 9),
            bg="white",
            fg="#6b7280"
        )
        self.status_label.pack()
        
        # Results frame
        results_frame = tk.LabelFrame(
            main_frame,
            text="🎯 Matching Results",
            font=("Arial", 12, "bold"),
            bg="white",
            padx=15,
            pady=15
        )
        results_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        # Scrollable results
        canvas_frame = tk.Frame(results_frame, bg="white")
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(canvas_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_text = tk.Text(
            canvas_frame,
            height=10,
            font=("Courier", 9),
            yscrollcommand=scrollbar.set,
            wrap=tk.WORD,
            bg="#f9fafb",
            relief=tk.FLAT
        )
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.results_text.yview)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
    
    def browse_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Reference Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.reference_image_path = file_path
            self.load_and_display_image(file_path)
            self.encode_reference_image()
            self.update_search_button_state()
    
    def load_and_display_image(self, path):
        try:
            image = Image.open(path)
            image.thumbnail((250, 250))
            photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=photo, text="")
            self.image_label.image = photo
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def encode_reference_image(self):
        try:
            image = face_recognition.load_image_file(self.reference_image_path)
            encodings = face_recognition.face_encodings(image)
            
            if len(encodings) == 0:
                messagebox.showwarning(
                    "No Face Detected",
                    "No face was detected in the selected image. Please choose another image."
                )
                self.reference_encoding = None
            else:
                self.reference_encoding = encodings[0]
                messagebox.showinfo(
                    "Success",
                    f"Face detected! Found {len(encodings)} face(s) in the image.\nUsing the first face for matching."
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process image: {str(e)}")
            self.reference_encoding = None
    
    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Folder to Search")
        if folder:
            self.folder_path = folder
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder)
            self.update_search_button_state()
    
    def update_search_button_state(self):
        if self.reference_encoding is not None and self.folder_path:
            self.search_btn.config(state=tk.NORMAL)
        else:
            self.search_btn.config(state=tk.DISABLED)
    
    def search_faces(self):
        if not self.reference_encoding:
            messagebox.showerror("Error", "Please select a valid reference image first!")
            return
        
        if not self.folder_path:
            messagebox.showerror("Error", "Please select a folder to search!")
            return
        
        # Run search in a separate thread
        self.search_btn.config(state=tk.DISABLED)
        self.progress.start()
        self.status_label.config(text="Searching...")
        self.results_text.delete(1.0, tk.END)
        
        thread = threading.Thread(target=self.perform_search, daemon=True)
        thread.start()
    
    def perform_search(self):
        self.matches = []
        supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
        
        # Walk through all files in the directory
        for root, dirs, files in os.walk(self.folder_path):
            for file in files:
                if file.lower().endswith(supported_formats):
                    file_path = os.path.join(root, file)
                    self.status_label.config(text=f"Checking: {file}")
                    
                    try:
                        image = face_recognition.load_image_file(file_path)
                        encodings = face_recognition.face_encodings(image)
                        
                        for encoding in encodings:
                            # Compare faces
                            results = face_recognition.compare_faces([self.reference_encoding], encoding, tolerance=0.6)
                            if results[0]:
                                # Calculate face distance (lower is better match)
                                distance = face_recognition.face_distance([self.reference_encoding], encoding)[0]
                                confidence = (1 - distance) * 100
                                
                                self.matches.append({
                                    'filename': file,
                                    'path': file_path,
                                    'confidence': confidence
                                })
                                break
                    except Exception as e:
                        print(f"Error processing {file_path}: {str(e)}")
        
        # Update UI in main thread
        self.root.after(0, self.display_results)
    
    def open_file_location(self, file_path):
        """Open the file location in the system's file explorer"""
        import platform
        import subprocess
        
        try:
            system = platform.system()
            if system == 'Windows':
                subprocess.run(['explorer', '/select,', file_path])
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', '-R', file_path])
            else:  # Linux
                folder_path = os.path.dirname(file_path)
                subprocess.run(['xdg-open', folder_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file location: {str(e)}")
    
    def open_image(self, file_path):
        """Open the image in the default image viewer"""
        import platform
        import subprocess
        
        try:
            system = platform.system()
            if system == 'Windows':
                os.startfile(file_path)
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', file_path])
            else:  # Linux
                subprocess.run(['xdg-open', file_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open image: {str(e)}")
    
    def display_results(self):
        self.progress.stop()
        self.search_btn.config(state=tk.NORMAL)
        self.status_label.config(text="")
        
        # Clear previous results
        for widget in self.results_text.winfo_children():
            widget.destroy()
        
        self.results_text.delete(1.0, tk.END)
        
        if not self.matches:
            self.results_text.insert(tk.END, "No matching faces found in the selected folder.")
            messagebox.showinfo("Search Complete", "No matching faces were found.")
        else:
            # Sort by confidence
            self.matches.sort(key=lambda x: x['confidence'], reverse=True)
            
            self.results_text.insert(tk.END, f"Found {len(self.matches)} matching image(s):\n\n")
            self.results_text.insert(tk.END, "=" * 80 + "\n\n")
            
            for i, match in enumerate(self.matches, 1):
                # Insert match info
                self.results_text.insert(tk.END, f"Match #{i}:\n")
                self.results_text.insert(tk.END, f"  Filename: {match['filename']}\n")
                self.results_text.insert(tk.END, f"  Location: {match['path']}\n")
                self.results_text.insert(tk.END, f"  Confidence: {match['confidence']:.2f}%\n")
                
                # Add clickable buttons for this match
                button_start = self.results_text.index(tk.END)
                self.results_text.insert(tk.END, "  ")
                
                # Create frame for buttons
                btn_frame = tk.Frame(self.results_text, bg="#f9fafb")
                
                # Open Image button
                open_img_btn = tk.Button(
                    btn_frame,
                    text="📷 Open Image",
                    command=lambda p=match['path']: self.open_image(p),
                    bg="#3b82f6",
                    fg="white",
                    font=("Arial", 8, "bold"),
                    padx=8,
                    pady=3,
                    cursor="hand2",
                    relief=tk.RAISED
                )
                open_img_btn.pack(side=tk.LEFT, padx=2)
                
                # Open Location button
                open_loc_btn = tk.Button(
                    btn_frame,
                    text="📁 Open Location",
                    command=lambda p=match['path']: self.open_file_location(p),
                    bg="#10b981",
                    fg="white",
                    font=("Arial", 8, "bold"),
                    padx=8,
                    pady=3,
                    cursor="hand2",
                    relief=tk.RAISED
                )
                open_loc_btn.pack(side=tk.LEFT, padx=2)
                
                # Copy Path button
                copy_btn = tk.Button(
                    btn_frame,
                    text="📋 Copy Path",
                    command=lambda p=match['path']: self.copy_to_clipboard(p),
                    bg="#8b5cf6",
                    fg="white",
                    font=("Arial", 8, "bold"),
                    padx=8,
                    pady=3,
                    cursor="hand2",
                    relief=tk.RAISED
                )
                copy_btn.pack(side=tk.LEFT, padx=2)
                
                # Embed the button frame in the text widget
                self.results_text.window_create(tk.END, window=btn_frame)
                self.results_text.insert(tk.END, "\n\n" + "-" * 80 + "\n\n")
            
            messagebox.showinfo(
                "Search Complete",
                f"Found {len(self.matches)} matching image(s)!\nCheck the results below."
            )
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.status_label.config(text="Path copied to clipboard!", fg="#10b981")
        self.root.after(2000, lambda: self.status_label.config(text="", fg="#6b7280"))

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.mainloop()
