from flask import Flask, request, send_from_directory, render_template_string
import qrcode, os

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML_FORM = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>PDF to QR Generator</title>
  <style>
    body { font-family: Arial; margin: 50px; text-align:center; }
    form { margin: 20px auto; border: 1px solid #ccc; padding: 20px; width: 300px; border-radius: 8px; }
  </style>
</head>
<body>
  <h2>Upload PDF → Get QR Code</h2>
  <form method="post" enctype="multipart/form-data">
    <input type="file" name="pdf" accept="application/pdf" required><br><br>
    <button type="submit">Upload</button>
  </form>
  {% if qr_url %}
    <p><a href="{{ pdf_url }}" target="_blank">View PDF</a></p>
    <img src="{{ qr_url }}" width="200">
  {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    qr_url = pdf_url = None
    if request.method == "POST":
        file = request.files["pdf"]
        save_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(save_path)

        pdf_url = f"/api/uploads/{file.filename}"
        qr_img = qrcode.make(request.host_url.rstrip("/") + pdf_url)
        qr_filename = file.filename + ".png"
        qr_img.save(os.path.join(UPLOAD_FOLDER, qr_filename))
        qr_url = f"/api/uploads/{qr_filename}"

    return render_template_string(HTML_FORM, qr_url=qr_url, pdf_url=pdf_url)

@app.route("/uploads/<path:filename>")
def serve_uploads(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Vercel requires this
def handler(request, *args, **kwargs):
    return app(request, *args, **kwargs)