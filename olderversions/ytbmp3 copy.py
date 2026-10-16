import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import imageio_ffmpeg
import yt_dlp

# Set the overall theme color scheme
ctk.set_appearance_mode("System")  # Follows Windows Dark/Light mode
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

class ModernYoutubeDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("YouTube Media Downloader Pro")
        self.geometry("600x600")
        self.minsize(550, 550)
        
        # --- Variables ---
        self.download_folder = tk.StringVar()
        self.format_choice = tk.StringVar(value="mp3")
        self.video_quality = tk.StringVar(value="Medium (720p)")
        self.is_cancelled = False
        
        default_path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.download_folder.set(default_path)
        
        # --- UI Layout Design ---
        # 1. Title Banner
        self.title_label = ctk.CTkLabel(self, text="YouTube Downloader", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(padx=20, pady=(20, 10))
        
        # 2. Links Input Section
        self.links_label = ctk.CTkLabel(self, text="Paste YouTube Links (One per line):", font=ctk.CTkFont(size=13, weight="bold"))
        self.links_label.pack(anchor="w", padx=30, pady=(10, 5))
        
        self.links_text = ctk.CTkTextbox(self, height=120, font=("Consolas", 12))
        self.links_text.pack(fill="both", expand=True, padx=30, pady=5)
        self.links_text.insert("1.0", "https://www.youtube.com/watch?v=dQw4w9WgXcQ\n")
        
        # 3. Format Toggle Segment
        self.format_frame = ctk.CTkFrame(self)
        self.format_frame.pack(fill="x", padx=30, pady=10)
        
        self.lbl_format = ctk.CTkLabel(self.format_frame, text="Output Format:", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_format.pack(side="left", padx=15, pady=10)
        
        self.rad_mp3 = ctk.CTkRadioButton(self.format_frame, text="🎵 MP3 Audio", variable=self.format_choice, value="mp3", command=self.toggle_quality_menu)
        self.rad_mp3.pack(side="left", padx=15)
        
        self.rad_mp4 = ctk.CTkRadioButton(self.format_frame, text="🎬 MP4 Video", variable=self.format_choice, value="mp4", command=self.toggle_quality_menu)
        self.rad_mp4.pack(side="left", padx=15)
        
        # 4. Dynamic Video Quality Frame (Hidden by default, unrolls when MP4 chosen)
        self.quality_frame = ctk.CTkFrame(self)
        self.lbl_quality = ctk.CTkLabel(self.quality_frame, text="Video Quality Option:", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_quality.pack(side="left", padx=15, pady=10)
        
        self.quality_menu = ctk.CTkOptionMenu(self.quality_frame, values=["High (1080p+ / Best)", "Medium (720p)", "Low (480p)"], variable=self.video_quality)
        self.quality_menu.pack(side="left", padx=15, fill="x", expand=True)
        
        # 5. Save Destination Row
        self.folder_frame = ctk.CTkFrame(self)
        self.folder_frame.pack(fill="x", padx=30, pady=10)
        
        self.folder_entry = ctk.CTkEntry(self.folder_frame, textvariable=self.download_folder, font=("Arial", 11))
        self.folder_entry.pack(side="left", padx=(15, 5), pady=10, fill="x", expand=True)
        
        self.browse_btn = ctk.CTkButton(self.folder_frame, text="📁 Browse USB", width=110, command=self.browse_folder)
        self.browse_btn.pack(side="right", padx=(5, 15))
        
        # 6. Progress Engine Displays
        self.status_label = ctk.CTkLabel(self, text="Status: Ready", font=ctk.CTkFont(slant="italic"), text_color="gray")
        self.status_label.pack(pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(self, mode="indeterminate")
        
        # 7. Execution Controls Action Buttons
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(fill="x", padx=30, pady=(10, 25))
        
        self.convert_btn = ctk.CTkButton(self.btn_frame, text="🚀 Start Download", font=ctk.CTkFont(size=14, weight="bold"), fg_color="#2ecc71", hover_color="#27ae60", height=45, command=self.start_download_thread)
        self.convert_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.stop_btn = ctk.CTkButton(self.btn_frame, text="🛑 Stop", font=ctk.CTkFont(size=14, weight="bold"), fg_color="#e74c3c", hover_color="#c0392b", height=45, width=120, command=self.stop_download)
        self.stop_btn.pack(side="right", padx=(5, 0))
        self.stop_btn.configure(state="disabled")

    def toggle_quality_menu(self):
        """Displays quality controls only when downloading full videos."""
        if self.format_choice.get() == "mp4":
            self.quality_frame.pack(fill="x", padx=30, pady=5, before=self.folder_frame)
        else:
            self.quality_frame.pack_forget()

    def browse_folder(self):
        selected_dir = filedialog.askdirectory(initialdir=self.download_folder.get())
        if selected_dir:
            self.download_folder.set(os.path.normpath(selected_dir))

    def start_download_thread(self):
        raw_text = self.links_text.get("1.0", "end-1c").strip()
        links = [line.strip() for line in raw_text.split("\n") if line.strip()]
        
        if not links:
            messagebox.showwarning("No Links", "Please paste at least one YouTube link.")
            return
            
        output_dir = self.download_folder.get().strip()
        
        self.is_cancelled = False
        self.convert_btn.configure(state="disabled", text="Processing Task...")
        self.stop_btn.configure(state="normal")
        self.progress_bar.pack(fill="x", padx=30, pady=5)
        self.progress_bar.start()
        
        thread = threading.Thread(target=self.process_downloads, args=(links, output_dir), daemon=True)
        thread.start()

    def stop_download(self):
        if messagebox.askyesno("Confirm Stop", "Do you want to cancel the download operations?"):
            self.is_cancelled = True
            self.status_label.configure(text="Aborting operations... cleaning workspace.")
            self.stop_btn.configure(state="disabled")

    def yt_dlp_hook(self, d):
        if self.is_cancelled:
            raise Exception("User_Cancelled_Download")

        if d['status'] == 'downloading':
            filename = os.path.basename(d.get('filename', 'media_file'))
            clean_name = filename.rsplit('.', 1)[0][:35] + "..." if len(filename) > 35 else filename
            self.after(0, lambda: self.status_label.configure(text=f"Downloading: {clean_name}"))
        elif d['status'] == 'finished':
            self.after(0, lambda: self.status_label.configure(text="Finalizing formatting containers..."))

    def process_downloads(self, links, output_path):
        try:
            if not os.path.exists(output_path):
                os.makedirs(output_path)
                
            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
            chosen_format = self.format_choice.get()
            quality_selection = self.video_quality.get()
            
            ydl_opts = {
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'ffmpeg_location': ffmpeg_path,
                'ignoreerrors': True,
                'progress_hooks': [self.yt_dlp_hook],
            }
            
            if chosen_format == "mp3":
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '320',
                    }]
                })
            else:
                # Video quality filter definitions mapping based on selection
                if "High" in quality_selection:
                    # Fetches highest available resolution matching best audio
                    video_format_str = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                elif "Medium" in quality_selection:
                    # Limits cap stream resolution strict limit under or equal to 720p height configurations
                    video_format_str = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best'
                else:
                    # Small files resolution constraint limit cap strict max 480p height boundaries
                    video_format_str = 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best'
                
                ydl_opts.update({'format': video_format_str})
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download(links)
                
            if self.is_cancelled:
                raise Exception("User_Cancelled_Download")
                
            self.after(0, self.download_finished, "success", f"Done! Files safely written to target:\n{output_path}")
            
        except Exception as e:
            if "User_Cancelled_Download" in str(e):
                self.after(0, self.download_finished, "cancelled", "Operations cancelled successfully.")
            elif isinstance(e, PermissionError):
                self.after(0, self.download_finished, "error", "Windows blocked folder write capabilities. Check path setup.")
            else:
                self.after(0, self.download_finished, "error", f"An unexpected failure event popped up:\n{str(e)}")

    def download_finished(self, status, message):
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.convert_btn.configure(state="normal", text="🚀 Start Download")
        self.stop_btn.configure(state="disabled")
        self.status_label.configure(text="Status: Ready")
        
        if status == "success":
            messagebox.showinfo("Success", message)
        elif status == "cancelled":
            messagebox.showwarning("Cancelled", message)
        else:
            messagebox.showerror("Error", message)

if __name__ == "__main__":
    app = ModernYoutubeDownloader()
    app.mainloop()