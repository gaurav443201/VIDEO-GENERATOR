from flask import Flask, render_template, request, redirect, url_for, jsonify
import uuid
from werkzeug.utils import secure_filename
import os
import json
import time
import shutil

UPLOAD_FOLDER = 'user_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("static/reels", exist_ok=True)

JOBS_FILE = 'jobs.json'


def load_jobs():
    if not os.path.exists(JOBS_FILE):
        return []
    try:
        with open(JOBS_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return []


def save_jobs(jobs):
    try:
        with open(JOBS_FILE, 'w') as f:
            json.dump(jobs, f, indent=4)
    except Exception as e:
        print(f"Error saving jobs: {e}")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/jobs")
def get_jobs_api():
    return jsonify({"jobs": load_jobs()})


@app.route("/create", methods=["GET", "POST"])
def create():
    myid = str(uuid.uuid1())
    if request.method == "POST":
        rec_id = request.form.get("uuid")
        desc = request.form.get("text", "")
        voice_id = request.form.get("voice", "pNInz6obpgDQGcFmaJgB")
        bg_music = request.form.get("bg_music", "none")
        bg_music_volume = float(request.form.get("bg_music_volume", "0.15"))
        
        input_files = []
        
        # Create folder for this job
        job_dir = os.path.join(app.config['UPLOAD_FOLDER'], rec_id)
        os.makedirs(job_dir, exist_ok=True)
        
        # Save files
        for key in request.files:
            file = request.files[key]
            if file and file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(job_dir, filename))
                input_files.append(filename)
        
        # Write description and input files config
        with open(os.path.join(job_dir, "desc.txt"), "w", encoding="utf-8") as f:
            f.write(desc)
            
        with open(os.path.join(job_dir, "input.txt"), "w", encoding="utf-8") as f:
            for fl in input_files:
                f.write(f"file '{fl}'\nduration 2\n")  # default to 2 seconds per image for better viewing
                
        # Write job configuration file for worker
        job_config = {
            "id": rec_id,
            "text": desc,
            "voice": voice_id,
            "bg_music": bg_music,
            "bg_music_volume": bg_music_volume,
            "files": input_files
        }
        with open(os.path.join(job_dir, "job.json"), "w", encoding="utf-8") as f:
            json.dump(job_config, f, indent=4)
            
        # Append to global jobs.json queue
        jobs = load_jobs()
        if not any(j['id'] == rec_id for j in jobs):
            jobs.append({
                "id": rec_id,
                "text": desc,
                "voice": voice_id,
                "bg_music": bg_music,
                "bg_music_volume": bg_music_volume,
                "status": "pending",
                "created_at": int(time.time()),
                "error": None,
                "files_count": len(input_files)
            })
            save_jobs(jobs)
            
        return redirect(url_for("create", success=rec_id))
        
    # GET request
    jobs = load_jobs()
    recent_jobs = sorted(jobs, key=lambda x: x.get('created_at', 0), reverse=True)[:5]
    success_id = request.args.get("success")
    return render_template("create.html", myid=myid, recent_jobs=recent_jobs, success_id=success_id)


@app.route("/gallery")
def gallery():
    reels_dir = "static/reels"
    os.makedirs(reels_dir, exist_ok=True)
    reels = [r for r in os.listdir(reels_dir) if r.endswith(".mp4")]
    
    # We want to match reels with their jobs.json data so we can display captions
    jobs = load_jobs()
    jobs_map = {j['id']: j for j in jobs}
    
    gallery_items = []
    for reel in reels:
        job_id = reel.replace(".mp4", "")
        job_info = jobs_map.get(job_id, {
            "id": job_id,
            "text": "Created Video",
            "bg_music": "none"
        })
        gallery_items.append({
            "filename": reel,
            "id": job_id,
            "text": job_info.get("text", "Created Video"),
            "bg_music": job_info.get("bg_music", "none")
        })
        
    return render_template("gallery.html", items=gallery_items)


@app.route("/delete/<job_id>", methods=["POST"])
def delete_reel(job_id):
    # Remove from static/reels/
    reel_path = os.path.join("static", "reels", f"{job_id}.mp4")
    if os.path.exists(reel_path):
        try:
            os.remove(reel_path)
        except Exception as e:
            print(f"Error removing reel file: {e}")
            
    # Remove from user_uploads/
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], job_id)
    if os.path.exists(upload_path):
        try:
            shutil.rmtree(upload_path)
        except Exception as e:
            print(f"Error removing upload dir: {e}")
            
    # Remove from jobs.json
    jobs = load_jobs()
    jobs = [j for j in jobs if j['id'] != job_id]
    save_jobs(jobs)
    
    # Remove from done.txt
    if os.path.exists("done.txt"):
        try:
            with open("done.txt", "r") as f:
                done_lines = f.readlines()
            with open("done.txt", "w") as f:
                for line in done_lines:
                    if line.strip() != job_id:
                        f.write(line)
        except Exception as e:
            print(f"Error updating done.txt: {e}")
            
    return redirect(url_for("gallery"))


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))