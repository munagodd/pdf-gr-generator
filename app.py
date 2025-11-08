from flask import Flask, request, render_template
import os, json, qrcode
from io import BytesIO
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

app = Flask(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

def get_drive_service():
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not creds_json:
        raise Exception("❌ Missing GOOGLE_CREDENTIALS_JSON environment variable.")
    
    creds_dict = json.loads(creds_json)
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    service = build("drive", "v3", credentials=creds)
    return service

def upload_file_to_drive(service, file_bytes, filename, mimetype="application/octet-stream", folder_id=None):
    """Uploads a file to Google Drive and returns the file ID and shareable link."""
    file_metadata = {"name": filename}
    if folder_id:
        file_metadata["parents"] = [folder_id]

    media = MediaIoBaseUpload(file_bytes, mimetype=mimetype, resumable=True)
    drive_file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    file_id = drive_file.get("id")

    # Make file public
    service.permissions().create(
        fileId=file_id,
        body={"role": "reader", "type": "anyone"}
    ).execute()

    file_url = f"https://drive.google.com/uc?id={file_id}&export=download"
    return file_id, file_url

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        pdf = request.files.get("pdf")
        if pdf:
            service = get_drive_service()

            # Upload PDF
            pdf_bytes = BytesIO(pdf.read())
            pdf_id, pdf_url = upload_file_to_drive(service, pdf_bytes, pdf.filename, mimetype="application/pdf")

            # Generate QR code for PDF
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=15,
                border=4
            )
            qr.add_data(pdf_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            qr_bytes = BytesIO()
            img.save(qr_bytes, format="PNG")
            qr_bytes.seek(0)

            qr_id, qr_url = upload_file_to_drive(service, qr_bytes, f"QR_{pdf.filename}.png", mimetype="image/png")

            return render_template("index.html", pdf_url=pdf_url, qr_url=qr_url)

    return render_template("index.html", pdf_url=None, qr_url=None)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)