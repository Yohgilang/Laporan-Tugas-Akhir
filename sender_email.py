# Library konfigurasi email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from dotenv import load_dotenv
import os


# Memuat variabel dalam file .env
load_dotenv()

# Konfigurasi email
email_username = os.getenv("EMAIL_USERNAME")
email_password = os.getenv("EMAIL_PASSWORD")
email_host = os.getenv("EMAIL_HOST")
email_port = os.getenv("EMAIL_PORT")

# Fungsi untuk mengirim email
def send_email(email_to):
    fromaddr = email_username
    toaddr = email_to

    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Hasil Deteksi Penyakit Tanaman Terung"

    body = "Berikut adalah hasil deteksi penyakit tanaman terung."
    msg.attach(MIMEText(body, 'plain'))
    filename = "hasil_deteksi_dan_counting.pdf" 
    attachment = open(filename, "rb")
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(part)
    server = smtplib.SMTP(email_host, email_port)
    server.starttls()
    server.login(fromaddr, email_password) 
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()
