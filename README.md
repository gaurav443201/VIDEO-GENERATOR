# 🌌 VidSnapAI - Cosmic Reel & Video Generator

VidSnapAI is a premium, high-performance web application designed to generate dynamic **9:16 vertical video reels** from uploaded image slides, synthesise customized text-to-speech voiceovers, and mix spatial backing soundtracks in real time. 

Featuring a premium **Dark Cyberpunk Glassmorphic** theme, a real-time progress-tracking dashboard, dynamic audio overlays, and a multi-service daemon architecture, VidSnapAI is built for performance and aesthetic excellence.

---

## ✨ Features

- **Cyberpunk Dark Mode & Glassmorphism UI:** Seamless radial gradients, blurred backdrops, neon highlights, and fluid micro-animations.
- **AI-Powered Voice Synthesis:** Integrated ElevenLabs low-latency voice synthesis with a robust fallback to Google Text-To-Speech (gTTS) to guarantee uptime.
- **Dynamic Soundtrack Mixer:** Select from ambient background tracks and adjust relative volume parameters processed through FFmpeg audio filter complexes.
- **Real-Time Render Queue Dashboard:** AJAX polling system monitoring the status of jobs (Pending ➡️ Processing ➡️ Completed / Failed) without page reloads.
- **TikTok/Reels Optimized:** Automatic image scaling to 1080x1920 with blurred pillar box pads for professional 9:16 layout formatting.
- **Multi-Service Deployment Ready:** Standardized container builds using Docker, docker-compose, and Render blueprints.

---

## 🛠️ Tech Stack

- **Backend Logic:** Python / Flask
- **Audio/Video Processing:** FFmpeg
- **Task Scheduling:** File-based queuing loop (`jobs.json`)
- **Voice Synthesis:** ElevenLabs API & gTTS
- **Frontend Design:** HTML5 / CSS3 (Vanilla Glassmorphic styling), Bootstrap 5, FontAwesome 6
- **Server Deployment:** Gunicorn / Docker

---

## 🚀 Local Installation

### Prerequisites
Make sure you have [Python 3.10+](https://www.python.org/) and [FFmpeg](https://ffmpeg.org/) installed globally and added to your system path.

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/gaurav443201/VIDEO-GENERATOR.git
   cd VIDEO-GENERATOR
   ```

2. **Install Python Packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Copy the template environment file:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and fill in your ElevenLabs API key:
   ```env
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
   PORT=5000
   ```

4. **Launch the Application:**
   You will need to run both the Web Server and the Queue Processing Daemon.
   
   - **Start the Web Server:**
     ```bash
     python main.py
     ```
     *The web client will be available at `http://127.0.0.1:5000`.*
     
   - **Start the Background Video Queue Worker:**
     ```bash
     python -u generate_process.py
     ```

---

## 🐳 Docker Deployment (Recommended)

To run the entire suite (Web server and worker daemon) side-by-side inside containers with shared volumes:

1. **Spin up the stack:**
   ```bash
   docker-compose up --build
   ```
2. **Access the application:** Open `http://localhost:5000` in your web browser.

---

## ☁️ Deploying to Render

This repository includes a `render.yaml` configuration for immediate deployment on Render:

1. Connect your GitHub repository to **Render**.
2. Create a new **Blueprint Route**.
3. Choose this repository. Render will automatically parse `render.yaml` and set up the service.
4. Input your `ELEVENLABS_API_KEY` securely in the Render GUI dashboard under Environment Settings.