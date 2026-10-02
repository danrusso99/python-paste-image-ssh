import getpass
import io
import os
import sys
from datetime import datetime
from pathlib import Path

import paramiko
import pyperclip
from dotenv import load_dotenv
from PIL import Image, ImageGrab

load_dotenv(Path(__file__).parent / ".env")

HOST = os.environ["SSH_HOST"]
USER = os.environ["SSH_USER"]
PASSWORD = os.getenv("SSH_PASSWORD")  # opcional
REMOTE_DIR = os.getenv("REMOTE_DIR", "/tmp/screenshots")

# 1. Imagen del portapapeles
img = ImageGrab.grabclipboard()
if not isinstance(img, Image.Image):
    sys.exit("No hay ninguna imagen en el portapapeles (Win+Shift+S).")

buf = io.BytesIO()
img.save(buf, "PNG")
buf.seek(0)

name = f"screenshot-{datetime.now():%Y%m%d-%H%M%S}.png"
remote_path = f"{REMOTE_DIR}/{name}"

# 2. Una sola conexión: se usa llave si existe, si no pide contraseña
client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

if PASSWORD:
    client.connect(
        HOST,
        username=USER,
        password=PASSWORD,
        look_for_keys=False,
        allow_agent=False,
        timeout=10,
    )
else:
    try:
        client.connect(HOST, username=USER, timeout=10)
    except paramiko.AuthenticationException:
        client.connect(
            HOST,
            username=USER,
            password=getpass.getpass("Password: "),
            look_for_keys=False,
            allow_agent=False,
            timeout=10,
        )

# 3. mkdir + subir + chmod, todo por la misma sesión
_, stdout, _ = client.exec_command(f"mkdir -p {REMOTE_DIR} && chmod 755 {REMOTE_DIR}")
stdout.channel.recv_exit_status()  # esperar a que termine

sftp = client.open_sftp()
sftp.putfo(buf, remote_path)
sftp.chmod(remote_path, 0o644)
sftp.close()
client.close()

# 4. Ruta al portapapeles
pyperclip.copy(remote_path)
print(f"Listo: {remote_path}")
