from flask import Flask, request, send_from_directory, render_template_string, url_for
import os
import qrcode
from qrcode.image.pil import PilImage

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        pdf = request.files["pdf"]
        if pdf:
            # Save the uploaded PDF
            filepath = os.path.join(UPLOAD_FOLDER, pdf.filename)
            pdf.save(filepath)

            # Generate viewer URL (not direct PDF)
            viewer_url = url_for("view_pdf", filename=pdf.filename, _external=True)

            # Generate high-resolution PNG QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=15,   # bigger box size = higher resolution
                border=4,
            )
            qr.add_data(viewer_url)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white", image_factory=PilImage)
            png_filename = f"{pdf.filename}_qr.png"
            png_path = os.path.join(UPLOAD_FOLDER, png_filename)
            img.save(png_path)

            # Return HTML with QR + links
            return f"""
            <h2>✅ QR Code Generated Successfully!</h2>
            <p>Scan this QR code to view your PDF in the browser:</p>
            <img src='/uploads/{png_filename}' width='250' height='250' alt='QR Code'><br><br>

            <a href='/uploads/{png_filename}' download>⬇️ Download PNG QR Code</a><br>
            <a href='{viewer_url}' target='_blank'>📄 View PDF in Browser</a><br>
            <a href='/'>🔁 Upload Another PDF</a>
            """

    # Default upload form
    return render_template_string("""
    <h2>📤 Upload PDF to Generate QR Code</h2>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="pdf" accept="application/pdf" required>
        <button type="submit">Upload & Generate QR</button>
    </form>
    """)


@app.route("/view/<path:filename>")
def view_pdf(filename):
    """Display a webpage that embeds the uploaded PDF."""
    pdf_url = url_for("serve_file", filename=filename, _external=True)
    return render_template_string(f"""
    <html>
      <head>
        <title>Document Viewer</title>
        <style>
          body {{
            font-family: Arial, sans-serif;
            text-align: center;
            background-color: #f7f7f7;
            margin: 20px;
          }}
          iframe {{
            border: 2px solid #ccc;
            border-radius: 10px;
            width: 90%;
            height: 800px;
          }}
        </style>
      </head>
      <body>
        <h2>📄 Viewing: {filename}</h2>
        <iframe src="{pdf_url}" allowfullscreen></iframe>
        <p><a href="/">⬅️ Back to Upload Page</a></p>
      </body>
    </html>
    """)


@app.route("/uploads/<path:filename>")
def serve_file(filename):
    """Serve uploaded files (PDFs and PNGs) inline in browser."""
    if filename.lower().endswith(".pdf"):
        mimetype = "application/pdf"
    elif filename.lower().endswith(".png"):
        mimetype = "image/png"
    else:
        mimetype = "application/octet-stream"

    response = send_from_directory(
        UPLOAD_FOLDER,
        filename,
        as_attachment=False,
        mimetype=mimetype
    )
    response.headers["Content-Disposition"] = f'inline; filename="{filename}"'
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))