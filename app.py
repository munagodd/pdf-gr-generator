from flask import Flask, request, send_from_directory, render_template, url_for
import os, qrcode
from qrcode.image.svg import SvgImage

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
            svg_filename = f"{pdf.filename}_qr.svg"
            svg_path = os.path.join(UPLOAD_FOLDER, svg_filename)

            img = qrcode.make(file_url, image_factory=SvgImage)
            img.save(svg_path)
            return f"""
            <p>QR code generated!</p>
            <object data='/uploads/{svg_filename}' type='image/svg+xml' width='250' height='250'></object>            """
    return render_template("index.html")

@app.route("/uploads/<path:filename>")
def serve_pdf(filename):
    return send_from_directory(
        UPLOAD_FOLDER,
        filename,
        as_attachment=False,   # 👈 prevents download
        mimetype="application/pdf"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)