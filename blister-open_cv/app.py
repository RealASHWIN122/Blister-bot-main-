from flask import Flask, render_template, request, send_from_directory
import os
from detector import detect_blisters

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["image"]

    if file.filename == "":
        return "No file selected"

    upload_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )

    file.save(upload_path)

    output_path = os.path.join(
        app.config["OUTPUT_FOLDER"],
        file.filename
    )

    detect_blisters(upload_path, output_path)

    # Normalize path separator for web URLs across platforms
    result_url = output_path.replace("\\", "/")

    return render_template(
        "index.html",
        result=result_url
    )


@app.route("/outputs/<path:filename>")
def send_output(filename):
    return send_from_directory(app.config["OUTPUT_FOLDER"], filename)


if __name__ == "__main__":
    app.run(debug=True)
