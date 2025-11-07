from flask import Flask, request, send_from_directory, render_template, url_for, Response
import os
import qrcode
from qrcode.image.svg import SvgImage

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        pdf = request.files.get("pdf")
        if pdf:
            # Save uploaded PDF
            filepath = os.path.join(UPLOAD_FOLDER, pdf.filename)
            pdf.save(filepath)

            # Create URL to access the PDF
            file_url = url_for("serve_file", filename=pdf.filename, _external=True)

            # Generate SVG QR code
            svg_filename = f"{pdf.filename}_qr.svg"
            svg_path = os.path.join(UPLOAD_FOLDER, svg_filename)
            img = qrcode.make(file_url, image_factory=SvgImage)
            img.save(svg_path)

            # Return QR display page
            html = f"""
            <html>
            <body style="font-family:sans-serif;">
                <p><b>QR code generated successfully!</b></p>
                <p>Scan this QR code to view your PDF:</p>
                <object data='/uploads/{svg_filename}' type='image/svg+xml' width='250' height='250'></object>
                <p><a href='/uploads/{pdf.filename}' target='_blank'>View PDF in browser</a></p>
            </body>
            </html>
            """
            return Response(html, mimetype="text/html")

    return render_template("index.html")


@app.route("/uploads/<path:filename>")
def serve_file(filename):
    # Detect file type dynamically
    if filename.lower().endswith(".svg"):
        mimetype = "image/svg+xml"
    elif filename.lower().endswith(".pdf"):
        mimetype = "application/pdf"
    else:
        mimetype = "application/octet-stream"

    return send_from_directory(
        UPLOAD_FOLDER,
        filename,
        as_attachment=False,
        mimetype=mimetype
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)