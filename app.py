from flask import Flask, request, render_template, send_file
from pydub import AudioSegment
import whisper
import os
import uuid

app = Flask(__name__)
model = whisper.load_model("base")

UPLOAD_FOLDER = "uploads"
TRANSCRIPT_FOLDER = "transcripts"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TRANSCRIPT_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    transcript_text = None
    transcript_file = None
    if request.method == "POST":
        file = request.files["audio"]
        if file:
            unique_id = str(uuid.uuid4())
            mp3_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}.mp3")
            wav_path = mp3_path.replace(".mp3", ".wav")
            file.save(mp3_path)

            audio = AudioSegment.from_mp3(mp3_path)
            audio.export(wav_path, format="wav")

            result = model.transcribe(wav_path)
            transcript_text = result["text"]

            transcript_file = os.path.join(TRANSCRIPT_FOLDER, f"{unique_id}.txt")
            with open(transcript_file, "w", encoding="utf-8") as f:
                f.write(transcript_text)
            # Delete audio files after transcription
            try:
                if os.path.exists(mp3_path):
                    os.remove(mp3_path)
                if os.path.exists(wav_path):
                    os.remove(wav_path)
            except Exception as e:
                print(f"Error deleting files: {e}")

    return render_template("index.html",
                           transcript=transcript_text,
                           transcript_file=transcript_file)

@app.route("/download/<path:filename>")
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)