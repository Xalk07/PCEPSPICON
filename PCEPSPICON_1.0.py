import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk, ImageOps
import base64
import io
import os
import sys

def resource_path(relative_path):
    """ Получить абсолютный путь к ресурсу, работает и в .py, и в .exe """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class ImageInserterApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("PCEPSPICON")
        self.geometry("262x200")
        self.resizable(False, False)
        self.configure(padx=10, pady=10)

        # Загрузим base64 из файла
        self.base64_image = self.load_base64_from_file()

        imageic = self.decode_base64_image(self.base64_image[3])
        photo = ImageTk.PhotoImage(imageic)
        self.iconphoto(True, photo)

        # Containers
        self.top_frame = tk.Frame(self)
        self.top_frame.pack(fill="both", expand=True)

        self.left_frame = tk.Frame(self.top_frame)
        self.left_frame.pack(side="left", padx=10)

        self.center_frame = tk.Frame(self.top_frame, width=50)
        self.center_frame.pack(side="left")

        self.right_frame = tk.Frame(self.top_frame)
        self.right_frame.pack(side="left", padx=10)

        self.bottom_frame = tk.Frame(self)
        self.bottom_frame.pack(fill="x", pady=10)

        # LEFT: one unified canvas
        self.left_canvas = tk.Canvas(self.left_frame, width=80, height=80, bg="white",
                                     highlightthickness=1, highlightbackground="black", cursor="hand2")
        self.left_canvas.pack()

        # Add 📷 icon and text
        self.icon_text_id = self.left_canvas.create_text(40, 28, text="📷", font=("Arial", 20))
        self.drop_text_id = self.left_canvas.create_text(40, 55, text="Drop or click", font=("Arial", 7), fill="gray")

        # Register drag and drop directly on canvas
        self.left_canvas.drop_target_register(DND_FILES)
        self.left_canvas.dnd_bind('<<Drop>>', self.on_drop)

        # Bind left click to open file dialog
        self.left_canvas.bind("<Button-1>", lambda e: self.browse_file())

        # Center Arrow
        self.arrow_label = tk.Label(self.center_frame, text="→", font=("Arial", 24))
        self.arrow_label.pack(pady=20)

        # Right Canvas
        self.right_canvas = tk.Canvas(self.right_frame, width=80, height=80, bg="white")
        self.right_canvas.pack()

        # В __init__(), в self.bottom_frame ДО save_button:

        self.frame_var = tk.IntVar(value=1)

        self.bottom_frame = tk.Frame(self)
        self.bottom_frame.pack(fill="x", pady=10)

        # Радиокнопки — сверху
        self.radio_frame = tk.Frame(self.bottom_frame)
        self.radio_frame.pack(side="top")

        tk.Label(self.radio_frame, text="Choose Frame:").pack(side="left")
        tk.Radiobutton(self.radio_frame, text="TG16", variable=self.frame_var, value=1,
                       command=self.update_preview).pack(side="left")
        tk.Radiobutton(self.radio_frame, text="PCE", variable=self.frame_var, value=2,
                       command=self.update_preview).pack(side="left")

        # Кнопка — снизу
        self.save_button = tk.Button(self.bottom_frame, text="Insert and Save", command=self.insert_and_save)
        self.save_button.pack(side="top", pady=(10, 0))

        self.uploaded_image = None
        self.left_preview = None
        self.right_preview = None
        self.output_index = 0

        self.display_template()

    def update_preview(self):
        try:
            frame_choice = self.frame_var.get()
            if frame_choice == 1:
                image = self.decode_base64_image(self.base64_image[0])
            elif frame_choice == 2 and len(self.base64_image) > 1:
                image = self.decode_base64_image(self.base64_image[1])
            else:
                return  # не обновляем, если рамки нет
            preview = image.resize((80, 80), Image.LANCZOS)
            self.right_preview = ImageTk.PhotoImage(preview)
            self.right_canvas.delete("all")
            self.right_canvas.create_image(40, 40, image=self.right_preview)
        except Exception as e:
            messagebox.showerror("Preview Error", str(e))

    def load_base64_from_file(self):
        try:
            file_path = resource_path("base64img.txt")
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
                if not lines:
                    raise ValueError("base64img.txt is empty.")
                return lines
        except FileNotFoundError:
            messagebox.showerror("Error", "base64img.txt not found.")
            self.quit()

    @staticmethod
    def decode_base64_image(base64_str):
        try:
            image_data = base64.b64decode(base64_str.strip())
            return Image.open(io.BytesIO(image_data)).convert("RGBA")
        except Exception as e:
            raise ValueError(f"Ошибка при декодировании base64: {e}")

    def display_template(self):
        try:
            image = self.decode_base64_image(self.base64_image[0])
            preview = image.resize((80, 80), Image.LANCZOS)
            self.right_preview = ImageTk.PhotoImage(preview)
            self.right_canvas.delete("all")
            self.right_canvas.create_image(40, 40, image=self.right_preview)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load base64 image:\n{e}")

    def show_left_preview(self):
        if self.uploaded_image:
            preview = self.uploaded_image.resize((80, 80), Image.LANCZOS)
            self.left_preview = ImageTk.PhotoImage(preview)
            self.left_canvas.delete("all")  # Remove 📷 icon
            self.left_canvas.create_image(40, 40, image=self.left_preview)

    def browse_file(self):
        file = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")])
        if file:
            self.load_image(file)

    def on_drop(self, event):
        file = event.data.strip("{}")
        self.load_image(file)

    def load_image(self, path):
        try:
            self.uploaded_image = Image.open(path).convert("RGBA")
            self.uploaded_image = ImageOps.exif_transpose(self.uploaded_image)
            self.show_left_preview()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load image:\n{e}")

    def insert_and_save(self):
        if self.uploaded_image is None:
            messagebox.showwarning("Missing image", "Please load an image first.")
            return

        try:
            frame_choice = self.frame_var.get()

            if frame_choice == 1:
                # СТАРАЯ логика
                template = self.decode_base64_image(self.base64_image[0])
                #resized = self.uploaded_image.resize((68, 51), Image.LANCZOS)
                resized = self.uploaded_image.resize((68, 51), Image.LANCZOS).convert("RGBA")
                white_bg = Image.new("RGBA", resized.size, (255, 255, 255, 255))
                white_bg.paste(resized, (0, 0), resized)
                resized = white_bg
                template.paste(resized, (6, 6), resized)

            elif frame_choice == 2:
                if len(self.base64_image) < 2:
                    messagebox.showerror("Error", "Second frame not available in base64 file.")
                    return

                # Рамка 2: используем логику из второго скрипта
                imageicon = self.decode_base64_image(self.base64_image[1])
                copyicon = imageicon.copy()

                #resized_image = self.uploaded_image.resize((60, 60), Image.LANCZOS)
                resized_image = self.uploaded_image.resize((60, 60), Image.LANCZOS).convert("RGBA")
                white_bg = Image.new("RGBA", resized_image.size, (255, 255, 255, 255))
                white_bg.paste(resized_image, (0, 0), resized_image)
                resized_image = white_bg

                copyicon.paste(resized_image, (14, 10), resized_image)

                # Опционально: если есть третий элемент, добавим круг
                if len(self.base64_image) >= 3:
                    circle = self.decode_base64_image(self.base64_image[2])
                    copyicon.paste(circle, (1, 30), circle)

                template = copyicon

            else:
                messagebox.showerror("Error", "Unknown frame selected.")
                return

            filename = self.get_next_filename()
            template.save(filename)

            # Обновление preview
            preview = template.resize((80, 80), Image.LANCZOS)
            self.right_preview = ImageTk.PhotoImage(preview)
            self.right_canvas.delete("all")
            self.right_canvas.create_image(40, 40, image=self.right_preview)

            messagebox.showinfo("Saved", f"Saved as {filename}\n\n"
                                         f"Xalk07 (+███❖) 2025")

        except Exception as e:
            messagebox.showerror("Insert Error", str(e))

    def get_next_filename(self):
        while True:
            fname = f"ICON0-{self.output_index}.png"
            if not os.path.exists(fname):
                return fname
            self.output_index += 1

if __name__ == "__main__":
    app = ImageInserterApp()
    app.mainloop()
