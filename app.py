from flask import Flask, request, send_from_directory, render_template_string, url_for
import os
import qrcode
from qrcode.image.svg import SvgImage

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        pdf = request.files["pdf"]
        if pdf:
            # Save uploaded PDF
            filepath = os.path.join(UPLOAD_FOLDER, pdf.filename)
            pdf.save(filepath)

            # Generate file URL for the PDF
            file_url = url_for("serve_pdf", filename=pdf.filename, _external=True)

            # Generate SVG QR code
            svg_filename = f"{pdf.filename}_qr.svg"
            svg_path = os.path.join(UPLOAD_FOLDER, svg_filename)
            img = qrcode.make(file_url, image_factory=SvgImage)
            img.save(svg_path)

            # Return HTML response
            return f"""
            <h2>✅ QR Code Generated Successfully!</h2>
            <p>Scan the QR code to open your uploaded PDF:</p>
            <object data='/uploads/{svg_filename}' type='image/svg+xml' width='250' height='250'></object>

            <p>
                <a href='/uploads/{svg_filename}' download>⬇️ Download SVG QR Code</a><br>
                <a href='{file_url}' target='_blank'>📄 View Uploaded PDF</a><br>
                <a href='/'>🔁 Upload Another PDF</a>
            </p>
            """

    # Default upload page
    return render_template_string("""
    <h2>📤 Upload PDF to Generate QR Code</h2>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="pdf" accept="application/pdf" required>
        <button type="submit">Upload & Generate QR</button>
    </form>
    """)


@app.route("/uploads/<path:filename>")
def serve_pdf(filename):
    """Serve uploaded files (PDFs and SVGs)."""
    mimetype = (
        "application/pdf" if filename.lower().endswith(".pdf") else "image/svg+xml"
    )
    return send_from_directory(
        UPLOAD_FOLDER,
        filename,
        as_attachment=False,
        mimetype=mimetype
    )


if __name__ == "__main__":
    # Use Render's assigned port or default to 5000
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))