# YouTube Media Downloader  🚀

A modern, fast, and feature-rich desktop application built with Python and CustomTkinter to download YouTube videos and playlists as MP3 audio or MP4 video files. Designed with a clean dark-mode user interface, real-time download tracking, quality customization, and batch playlist support.

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Features

- **🎵 Audio & Video Extraction:** Choose between high-quality **320kbps MP3 audio** or **MP4 video** formats.
- **⚙️ Dynamic Resolution Options:** Pick video output resolutions (High 1080p+, Medium 720p, Low 480p) to conserve bandwidth and storage space.
- **📊 Real-time Metrics & Progress Bar:** View live download speed, percentage, downloaded MBs vs. total MBs, and exact batch item counters (e.g., `Downloading (3 of 54)`).
- **🛑 Stop / Cancel Process:** Instantly and safely kill active download processes mid-operation without locking files or freezing the app.
- **🔍 YouTube Quick Search:** Integrated search bar opens YouTube results directly in your web browser for easy link discovery.
- **📂 Flexible Destinations:** Save downloaded media directly to your local computer folders or external USB flash drives.
- **🎨 Modern Dark UI:** Styled with CustomTkinter for sleek visual elements, responsive layouts, and auto-adapting themes.
- **🛡️ Duplicate Overwrite Protection:** Built-in safeguards ensure existing files are never overwritten when downloading tracks with identical names.

---

## 🛠️ Prerequisites & Installation

### Option 1: Run from Source Code

#### 1. Clone or Download the Project
```bash
git clone https://github.com/yourusername/youtube-downloader.git
cd youtube-downloader
```

#### 2. Set Up a Virtual Environment (Recommended)
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

#### 3. Install Dependencies
Install all required libraries via requirements.txt:
```powershell
pip install -r requirements.txt
```

#### 4. Launch the Application
```powershell
python ytbmp3.py
```

---

## 📦 Building the Standalone `.exe` Executable

You can compile the app into a single `.exe` file that runs on any Windows machine without needing Python installed.

1. Install **PyInstaller** inside your environment:
   ```powershell
   pip install pyinstaller
   ```

2. Run the compilation command:
   ```powershell
   & ".\.venv\Scripts\pyinstaller" --noconsole --onefile --collect-all imageio_ffmpeg --add-data ".\.venv\Lib\site-packages\customtkinter;customtkinter/" "ytbmp3.py"
   ```

3. Locate your compiled executable in the newly created **`dist/`** folder:
   ```text
   📁 project-root/
   ├── 📂 dist/
   │   └── ytbmp3.exe  <-- Standalone Application
   └── ytbmp3.py
   ```

---

## 📖 How to Use

1. **Paste Links:** Copy one or more YouTube URLs (or full playlist URLs) into the main text box (one link per line).
2. **Select Format:** Choose between **🎵 MP3 Audio** or **🎬 MP4 Video**.
3. **Select Quality (MP4 only):** If MP4 is chosen, pick your preferred resolution option (High, Medium, Low).
4. **Choose Save Destination:** Click **Browse USB / Folder** to select your USB drive or target folder.
5. **Start Downloading:** Click **🚀 Start Download**.
6. **Monitor / Stop:** Track your progress via the live percentage bar, MB metric counter, and item indicator. Click **🛑 Stop** at any time to abort the task safely.

---

## 👨‍💻 Author & Credits

- **Author:** [Orkhan Rajabov](https://github.com/OrkhanRajabov)
- **Engine:** Powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp), [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter), and [FFmpeg](https://ffmpeg.org/).

---

## 📜 License

This project is open-source and available under the [MIT License](LICENSE).