from flask import Flask, request, send_from_directory, render_template_string
import qrcode, os

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML = """
<!doctype html>
<html>
  <head><title>PDF → QR</title></head>
  <body style="font-family: sans-serif; text-align: center;">
    <h2>Upload PDF to generate QR</h2>
    <form method="post" enctype="multipart/form-data">
      <input type="file" name="pdf" accept="application/pdf" required><br><br>
      <button type="submit">Upload</button>
    </form>
    {% if qr %}
      <p><a href="{{ pdf }}">View PDF</a></p>
      <img src="{{ qr }}" width="200">
    {% endif %}
  </body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    pdf = qr = None
    if request.method == "POST":
        file = request.files["pdf"]
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)
        pdf = f"/api/uploads/{file.filename}"
        qr_img = qrcode.make(request.host_url.rstrip("/") + pdf)
        qr_path = os.path.join(UPLOAD_FOLDER, file.filename + ".png")
        qr_img.save(qr_path)
        qr = f"/api/uploads/{file.filename}.png"
    return render_template_string(HTML, pdf=pdf, qr=qr)

@app.route("/uploads/<path:filename>")
def serve_uploads(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

def handler(request, *args, **kwargs):
    return app(request, *args, **kwargs)