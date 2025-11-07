from flask import Flask, request, send_from_directory, render_template, url_for
import os, qrcode

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        pdf = request.files["pdf"]
        if pdf:
            filepath = os.path.join(UPLOAD_FOLDER, pdf.filename)
            pdf.save(filepath)
            file_url = url_for("serve_pdf", filename=pdf.filename, _external=True)
            qr = qrcode.make(file_url)
            qr_path = os.path.join(UPLOAD_FOLDER, f"{pdf.filename}_qr.png")
            qr.save(qr_path)
            return f"<p>QR generated!</p><img src='/uploads/{pdf.filename}_qr.png'>"
    return render_template("index.html")

@app.route("/uploads/<path:filename>")
def serve_pdf(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)