from flask import Flask, request, render_template, redirect, url_for
import os, qrcode
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

app = Flask(__name__)

# Scopes for Google Drive file upload & sharing
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_drive_service():
    """Authenticate with Google Drive and return the Drive service object"""
    creds = None
    # Token stores the user's access token; created on first run
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        pdf = request.files["pdf"]
        if pdf:
            # Save locally first
            os.makedirs("uploads", exist_ok=True)
            local_path = os.path.join("uploads", pdf.filename)
            pdf.save(local_path)

            # Upload to Google Drive
            service = get_drive_service()
            file_metadata = {"name": pdf.filename, "mimeType": "application/pdf"}
            media = MediaFileUpload(local_path, mimetype="application/pdf")
            drive_file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
            file_id = drive_file.get("id")

            # Make file public
            service.permissions().create(
                fileId=file_id,
                body={"role": "reader", "type": "anyone"}
            ).execute()

            # Get shareable link
            pdf_url = f"https://drive.google.com/uc?id={file_id}"

            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=15,
                border=4
            )
            qr.add_data(pdf_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            os.makedirs("static", exist_ok=True)
            qr_path = os.path.join("static", "qr_code.png")
            img.save(qr_path)

            return render_template("index.html", qr_path=qr_path, pdf_url=pdf_url)

    return render_template("index.html", qr_path=None)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)