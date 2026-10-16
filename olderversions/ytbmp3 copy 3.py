import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import webbrowser
import urllib.parse
import customtkinter as ctk
import imageio_ffmpeg
import yt_dlp

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class ModernYoutubeDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("YouTube Media Downloader Pro")
        self.geometry("620x660")
        self.minsize(580, 620)
        
        # --- Variables ---
        self.download_folder = tk.StringVar()
        self.format_choice = tk.StringVar(value="mp3")
        self.video_quality = tk.StringVar(value="Medium (720p)")
        self.search_query = tk.StringVar()
        self.is_cancelled = False
        
        default_path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.download_folder.set(default_path)
        
        # --- Top Bar (Header & Author Info) ---
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(fill="x", padx=20, pady=(15, 5))
        
        self.title_label = ctk.CTkLabel(self.top_frame, text="YouTube Downloader", font=ctk.CTkFont(size=22, weight="bold"))
        self.title_label.pack(side="left", padx=10)
        
        # Clickable Author Tag (Top Right)
        self.author_label = ctk.CTkLabel(
            self.top_frame, 
            text="author: akusbutreal", 
            font=ctk.CTkFont(size=12, weight="bold", underline=True),
            text_color="#3498db",
            cursor="hand2"
        )
        self.author_label.pack(side="right", padx=10, pady=5)
        self.author_label.bind("<Button-1>", lambda e: webbrowser.open("https://www.instagram.com/akusbutreal"))
        
        # --- YouTube Quick Search Tool ---
        self.search_frame = ctk.CTkFrame(self)
        self.search_frame.pack(fill="x", padx=30, pady=10)
        
        self.search_entry = ctk.CTkEntry(self.search_frame, textvariable=self.search_query, placeholder_text="Enter song or artist name to search on YouTube...")
        self.search_entry.pack(side="left", padx=(15, 5), pady=10, fill="x", expand=True)
        
        self.search_btn = ctk.CTkButton(self.search_frame, text="🔍 Search YouTube", width=140, fg_color="#ff0000", hover_color="#cc0000", font=ctk.CTkFont(weight="bold"), command=self.open_youtube_search)
        self.search_btn.pack(side="right", padx=(5, 15))
        
        # --- Links Input Section ---
        self.links_label = ctk.CTkLabel(self, text="Paste YouTube Links (One per line):", font=ctk.CTkFont(size=13, weight="bold"))
        self.links_label.pack(anchor="w", padx=30, pady=(10, 5))
        
        self.links_text = ctk.CTkTextbox(self, height=120, font=("Consolas", 12))
        self.links_text.pack(fill="both", expand=True, padx=30, pady=5)
        self.links_text.insert("1.0", "https://www.youtube.com/watch?v=dQw4w9WgXcQ\n")
        
        # Format Toggle Segment
        self.format_frame = ctk.CTkFrame(self)
        self.format_frame.pack(fill="x", padx=30, pady=10)
        
        self.lbl_format = ctk.CTkLabel(self.format_frame, text="Output Format:", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_format.pack(side="left", padx=15, pady=10)
        
        self.rad_mp3 = ctk.CTkRadioButton(self.format_frame, text="🎵 MP3 Audio", variable=self.format_choice, value="mp3", command=self.toggle_quality_menu)
        self.rad_mp3.pack(side="left", padx=15)
        
        self.rad_mp4 = ctk.CTkRadioButton(self.format_frame, text="🎬 MP4 Video", variable=self.format_choice, value="mp4", command=self.toggle_quality_menu)
        self.rad_mp4.pack(side="left", padx=15)
        
        # Dynamic Video Quality Frame
        self.quality_frame = ctk.CTkFrame(self)
        self.lbl_quality = ctk.CTkLabel(self.quality_frame, text="Video Quality Option:", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_quality.pack(side="left", padx=15, pady=10)
        
        self.quality_menu = ctk.CTkOptionMenu(self.quality_frame, values=["High (1080p+ / Best)", "Medium (720p)", "Low (480p)"], variable=self.video_quality)
        self.quality_menu.pack(side="left", padx=15, fill="x", expand=True)
        
        # Save Destination Row
        self.folder_frame = ctk.CTkFrame(self)
        self.folder_frame.pack(fill="x", padx=30, pady=10)
        
        self.folder_entry = ctk.CTkEntry(self.folder_frame, textvariable=self.download_folder, font=("Arial", 11))
        self.folder_entry.pack(side="left", padx=(15, 5), pady=10, fill="x", expand=True)
        
        self.browse_btn = ctk.CTkButton(self.folder_frame, text="📁 Browse USB", width=110, command=self.browse_folder)
        self.browse_btn.pack(side="right", padx=(5, 15))
        
        # --- Progress & Data Metrics Displays ---
        self.status_label = ctk.CTkLabel(self, text="Status: Ready", font=ctk.CTkFont(slant="italic"), text_color="gray")
        self.status_label.pack(pady=(10, 2))
        
        # Added dynamic Size Label (MB / MB details)
        self.size_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12, slant="italic"), text_color="#3498db")
        self.percentage_label = ctk.CTkLabel(self, text="0%", font=ctk.CTkFont(size=12, weight="bold"))
        
        self.progress_bar = ctk.CTkProgressBar(self, mode="determinate")
        self.progress_bar.set(0)
        
        # Execution Controls
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(fill="x", padx=30, pady=(10, 25))
        
        self.convert_btn = ctk.CTkButton(self.btn_frame, text="🚀 Start Download", font=ctk.CTkFont(size=14, weight="bold"), fg_color="#2ecc71", hover_color="#27ae60", height=45, command=self.start_download_thread)
        self.convert_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.stop_btn = ctk.CTkButton(self.btn_frame, text="🛑 Stop", font=ctk.CTkFont(size=14, weight="bold"), fg_color="#e74c3c", hover_color="#c0392b", height=45, width=120, command=self.stop_download)
        self.stop_btn.pack(side="right", padx=(5, 0))
        self.stop_btn.configure(state="disabled")

    def open_youtube_search(self):
        query = self.search_query.get().strip()
        if not query:
            messagebox.showwarning("Empty Search", "Please enter a search query first.")
            return
        # Encode search string to handle special text/spaces cleanly inside a web URL
        encoded_query = urllib.parse.quote(query)
        webbrowser.open(f"https://www.youtube.com/results?search_query={encoded_query}")

    def toggle_quality_menu(self):
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
        self.convert_btn.configure(state="disabled", text="Processing...")
        self.stop_btn.configure(state="normal")
        
        self.size_label.pack(pady=2)
        self.percentage_label.pack(pady=2)
        self.progress_bar.pack(fill="x", padx=30, pady=(0, 10))
        self.progress_bar.set(0)
        self.percentage_label.configure(text="0%")
        self.size_label.configure(text="0.00 MB / 0.00 MB")
        
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
            clean_name = filename.rsplit('.', 1)[0][:30] + "..." if len(filename) > 30 else filename
            
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded_bytes = d.get('downloaded_bytes', 0)
            
            # Convert raw file bits directly into readable Megabytes
            dl_mb = downloaded_bytes / (1024 * 1024)
            total_mb = total_bytes / (1024 * 1024) if total_bytes else 0
            
            if total_bytes:
                percentage = (downloaded_bytes / total_bytes) * 100
                progress_val = downloaded_bytes / total_bytes
                
                self.after(0, lambda p=progress_val, pct=percentage, d_mb=dl_mb, t_mb=total_mb: 
                           self.update_progress_ui(p, pct, clean_name, d_mb, t_mb))
            else:
                self.after(0, lambda: self.status_label.configure(text=f"Downloading: {clean_name}"))
                self.after(0, lambda: self.size_label.configure(text=f"{dl_mb:.2f} MB / Unknown"))
                
        elif d['status'] == 'finished':
            self.after(0, lambda: self.status_label.configure(text="Finalizing formatting containers..."))

    def update_progress_ui(self, bar_value, percent_value, track_title, dl_mb, total_mb):
        self.progress_bar.set(bar_value)
        self.percentage_label.configure(text=f"{int(percent_value)}%")
        self.size_label.configure(text=f"{dl_mb:.2f} MB / {total_mb:.2f} MB")
        self.status_label.configure(text=f"Downloading: {track_title}")

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
                if "High" in quality_selection:
                    video_format_str = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                elif "Medium" in quality_selection:
                    video_format_str = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best'
                else:
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
        self.progress_bar.pack_forget()
        self.percentage_label.pack_forget()
        self.size_label.pack_forget()
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