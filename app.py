from flask import Flask, request, render_template
import os, qrcode, cloudinary, cloudinary.uploader

app = Flask(__name__)

# ✅ Cloudinary configuration (replace with your actual credentials)
cloudinary.config(
    cloud_name="YOUR_CLOUD_NAME",
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET",
    secure=True
)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        pdf = request.files["pdf"]
        if pdf:
            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(
                pdf,
                resource_type="raw",   # ensures Cloudinary accepts PDF
                folder="pdf_qr_uploads"
            )

            pdf_url = upload_result["secure_url"]

            # Generate high-res QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=15,  # controls resolution
                border=4
            )
            qr.add_data(pdf_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            qr_path = os.path.join("static", "qr_code.png")
            os.makedirs("static", exist_ok=True)
            img.save(qr_path)

            return render_template("index.html", qr_path=qr_path, pdf_url=pdf_url)

    return render_template("index.html", qr_path=None)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)