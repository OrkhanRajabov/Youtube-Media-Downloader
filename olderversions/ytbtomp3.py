import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import imageio_ffmpeg
import yt_dlp

class YoutubeMp3App:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube to MP3 Converter")
        self.root.geometry("550x450")
        self.root.minsize(500, 400)
        
        # --- Variables ---
        self.download_folder = tk.StringVar()
        # Default to a local folder first to avoid permission errors
        default_path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.download_folder.set(default_path)
        
        # --- UI Layout ---
        # 1. Links Label & Text Box
        tk.Label(root, text="Paste YouTube Links (One per line):", font=("Arial", 10, "bold")).pack(anchor="w", padx=20, pady=(15, 5))
        
        self.links_text = tk.Text(root, height=10, width=60, font=("Arial", 10))
        self.links_text.pack(fill="both", expand=True, padx=20, pady=5)
        # Pre-populate sample text
        self.links_text.insert("1.0", "https://www.youtube.com/watch?v=dQw4w9WgXcQ\n")
        
        # 2. Destination Folder Selector
        folder_frame = tk.Frame(root)
        folder_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(folder_frame, text="Save to:", font=("Arial", 10, "bold")).pack(side="left")
        self.folder_entry = tk.Entry(folder_frame, textvariable=self.download_folder, font=("Arial", 9), width=40)
        self.folder_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        browse_btn = tk.Button(folder_frame, text="Browse USB/Folder", command=self.browse_folder)
        browse_btn.pack(side="right")
        
        # 3. Progress Status & Action Button
        self.status_label = tk.Label(root, text="Ready", fg="blue", font=("Arial", 9, "italic"))
        self.status_label.pack(pady=5)
        
        self.progress = ttk.Progressbar(root, orient="horizontal", mode="indeterminate")
        
        self.convert_btn = tk.Button(root, text="🎵 Convert to MP3", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", height=2, command=self.start_download_thread)
        self.convert_btn.pack(fill="x", padx=20, pady=(5, 20))

    def browse_folder(self):
        selected_dir = filedialog.askdirectory(initialdir=self.download_folder.get())
        if selected_dir:
            # Fix slash directions for Windows compatibility
            self.download_folder.set(os.path.normpath(selected_dir))

    def start_download_thread(self):
        # Read lines from text box and filter out empty lines
        raw_text = self.links_text.get("1.0", tk.END).strip()
        links = [line.strip() for line in raw_text.split("\n") if line.strip()]
        
        if not links:
            messagebox.showwarning("No Links", "Please paste at least one YouTube link.")
            return
            
        output_dir = self.download_folder.get().strip()
        if not output_dir:
            messagebox.showwarning("No Folder", "Please choose a save destination.")
            return

        # Disable button and start progress indicator
        self.convert_btn.config(state="disabled", text="Processing...")
        self.progress.pack(fill="x", padx=20, pady=5)
        self.progress.start(10)
        
        # Run downloading in the background so the window remains interactive
        thread = threading.Thread(target=self.process_downloads, args=(links, output_dir), daemon=True)
        thread.start()

    def process_downloads(self, links, output_path):
        try:
            if not os.path.exists(output_path):
                os.makedirs(output_path)
                
            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'ffmpeg_location': ffmpeg_path,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
                'ignoreerrors': True,
                # Simple custom progress updater sent to UI status label
                'progress_hooks': [self.yt_dlp_hook],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download(links)
                
            self.root.after(0, self.download_finished, True, f"Success! All music saved to:\n{output_path}")
            
        except PermissionError:
            self.root.after(0, self.download_finished, False, f"Permission Denied!\nWindows blocked saving to {output_path}.\nTry picking a standard folder or running VS Code as Administrator.")
        except Exception as e:
            self.root.after(0, self.download_finished, False, f"An error occurred: {str(e)}")

    def yt_dlp_hook(self, d):
        if d['status'] == 'downloading':
            filename = os.path.basename(d.get('filename', 'song'))
            # Cut off extension for nicer aesthetic display
            clean_name = filename.rsplit('.', 1)[0][:35] + "..." if len(filename) > 35 else filename
            self.root.after(0, lambda: self.status_label.config(text=f"Downloading: {clean_name}"))
        elif d['status'] == 'finished':
            self.root.after(0, lambda: self.status_label.config(text="Converting audio to MP3..."))

    def download_finished(self, success, message):
        # Stop loading progress bars and reset button
        self.progress.stop()
        self.progress.pack_forget()
        self.convert_btn.config(state="normal", text="🎵 Convert to MP3")
        self.status_label.config(text="Ready" if success else "Error occurred")
        
        if success:
            messagebox.showinfo("Finished", message)
        else:
            messagebox.showerror("Error", message)

if __name__ == "__main__":
    window = tk.Tk()
    app = YoutubeMp3App(window)
    window.mainloop()