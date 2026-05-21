import os
import json
import time
import subprocess
from text_to_audio import text_to_speech_file


def get_audio_duration(audio_path, text=""):
    try:
        command = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            audio_path
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=5)
        duration_str = result.stdout.strip()
        if duration_str:
            val = float(duration_str)
            if val > 0:
                print(f"Detected audio duration: {val:.3f}s via ffprobe")
                return val
    except Exception as e:
        print(f"Warning: Could not get audio duration via ffprobe: {e}")
    
    # Fallback to word-count estimation
    words = len(text.split()) if text else 1
    estimated = max(3.0, (words / 2.2) + 1.5)
    print(f"Using estimated audio duration: {estimated:.2f}s (words: {words})")
    return estimated


def update_job_status(job_id, status, error=None):
    try:
        if not os.path.exists("jobs.json"):
            return
        with open("jobs.json", "r") as f:
            jobs = json.load(f)
        for j in jobs:
            if j["id"] == job_id:
                j["status"] = status
                if error:
                    j["error"] = str(error)
                break
        with open("jobs.json", "w") as f:
            json.dump(jobs, f, indent=4)
    except Exception as e:
        print(f"Error updating job status: {e}")


def process_job(folder):
    print(f"\n========================================\nProcessing Job: {folder}")
    
    # Update status to processing
    update_job_status(folder, "processing")
    
    # Read job configuration if it exists
    config_path = f"user_uploads/{folder}/job.json"
    voice_id = "pNInz6obpgDQGcFmaJgB"  # Adam pre-made
    bg_music = "none"
    bg_music_volume = 0.15
    text = ""
    files = []
    
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                voice_id = config.get("voice", voice_id)
                bg_music = config.get("bg_music", bg_music)
                bg_music_volume = config.get("bg_music_volume", bg_music_volume)
                text = config.get("text", "")
                files = config.get("files", [])
        except Exception as e:
            print(f"Error reading job config: {e}")
            
    if not text:
        # Fallback to reading desc.txt directly
        desc_path = f"user_uploads/{folder}/desc.txt"
        if os.path.exists(desc_path):
            with open(desc_path, "r", encoding="utf-8") as f:
                text = f.read()
                
    if not text:
        text = "Created Video"
        
    try:
        # Step 1: Text to Speech
        print(f"Generating audio with voice '{voice_id}'...")
        text_to_speech_file(text, folder, voice_id)
        
        # Calculate dynamic slideshow durations to match audio length
        audio_path = f"user_uploads/{folder}/audio.mp3"
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found at {audio_path}")
            
        audio_duration = get_audio_duration(audio_path, text)
        
        if not files:
            # Fallback scan
            job_dir = f"user_uploads/{folder}"
            if os.path.exists(job_dir):
                for filename in sorted(os.listdir(job_dir)):
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                        files.append(filename)
                        
        if files:
            num_files = len(files)
            duration_per_image = max(0.1, audio_duration / num_files)
            print(f"Rewriting input.txt for {folder}: {num_files} files, duration per image: {duration_per_image:.3f}s (audio duration: {audio_duration:.3f}s)")
            
            input_txt_path = f"user_uploads/{folder}/input.txt"
            with open(input_txt_path, "w", encoding="utf-8") as f:
                for fl in files:
                    f.write(f"file '{fl}'\n")
                    f.write(f"duration {duration_per_image}\n")
                # Repeat the last file once more without duration to hold the frame
                f.write(f"file '{files[-1]}'\n")
        else:
            print(f"Warning: No image files found for job {folder}!")
            
        # Step 2: Stitch Video using FFmpeg
        print(f"Stitching video with background music '{bg_music}'...")
        
        bg_music_path = f"static/songs/{bg_music}.mp3"
        has_bg_music = bg_music != "none" and os.path.exists(bg_music_path)
        
        # Ensure output directory exists
        os.makedirs("static/reels", exist_ok=True)
        output_file = f"static/reels/{folder}.mp4"
        
        w = 720
        h = 1280
        vf_filter = f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:black"

        if has_bg_music:
            print(f"Mixing background music: {bg_music_path} at volume {bg_music_volume}")
            command = [
                "ffmpeg", "-y",
                "-threads", "1",
                "-f", "concat",
                "-safe", "0",
                "-i", f"user_uploads/{folder}/input.txt",
                "-i", f"user_uploads/{folder}/audio.mp3",
                "-i", bg_music_path,
                "-filter_complex", f"[2:a]volume={bg_music_volume}[bg];[1:a][bg]amix=inputs=2:duration=first[a]",
                "-map", "0:v",
                "-map", "[a]",
                "-vf", vf_filter,
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-tune", "stillimage",
                "-rc-lookahead", "0",
                "-g", "15",
                "-r", "15",
                "-c:a", "aac",
                "-shortest",
                "-pix_fmt", "yuv420p",
                output_file
            ]
        else:
            print("No background music. Rendering video with voiceover only...")
            command = [
                "ffmpeg", "-y",
                "-threads", "1",
                "-f", "concat",
                "-safe", "0",
                "-i", f"user_uploads/{folder}/input.txt",
                "-i", f"user_uploads/{folder}/audio.mp3",
                "-vf", vf_filter,
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-tune", "stillimage",
                "-rc-lookahead", "0",
                "-g", "15",
                "-r", "15",
                "-c:a", "aac",
                "-shortest",
                "-pix_fmt", "yuv420p",
                output_file
            ]
            
        print(f"Running command: {' '.join(command)}")
        subprocess.run(command, check=True)
        print(f"SUCCESS: Reel created for {folder}")
        
        # Update status to completed
        update_job_status(folder, "completed")
        return True
    except Exception as e:
        print(f"ERROR processing job {folder}: {e}")
        update_job_status(folder, "failed", error=e)
        return False


if __name__ == "__main__":
    print("VidSnapAI Video Processing Daemon Started")
    while True:
        try:
            # Poll jobs from jobs.json
            if os.path.exists("jobs.json"):
                with open("jobs.json", "r") as f:
                    jobs = json.load(f)
            else:
                jobs = []
                
            done_folders = []
            if os.path.exists("done.txt"):
                with open("done.txt", "r") as f:
                    done_folders = [line.strip() for line in f.readlines()]
            
            # Find jobs that are in "pending" status
            pending_jobs = [j for j in jobs if j.get("status") == "pending"]
            
            for job in pending_jobs:
                job_id = job["id"]
                success = process_job(job_id)
                if success:
                    # Write to done.txt
                    with open("done.txt", "a") as f:
                        f.write(job_id + "\n")
                        
            # Sleep before next poll
            time.sleep(2)
        except KeyboardInterrupt:
            print("Exiting...")
            break
        except Exception as e:
            print(f"Daemon Loop Error: {e}")
            time.sleep(5)