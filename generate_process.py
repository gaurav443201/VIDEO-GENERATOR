import os
import json
import time
import subprocess
from text_to_audio import text_to_speech_file


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
    
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                voice_id = config.get("voice", voice_id)
                bg_music = config.get("bg_music", bg_music)
                bg_music_volume = config.get("bg_music_volume", bg_music_volume)
                text = config.get("text", "")
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