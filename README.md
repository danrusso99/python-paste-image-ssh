# paste-image-ssh

Script en Python para Windows que toma la **imagen que tienes en el portapapeles** (por ejemplo una captura con `Win+Shift+S`), la sube a un servidor remoto por **SFTP usando una sola conexión SSH** y deja la **ruta remota en el portapapeles**, lista para pegarla en tu sesión SSH/tmux (por ejemplo dentro de `opencode`).

## Cómo funciona

1. Lee la imagen del portapapeles y la convierte a PNG en memoria.
2. Abre **una sola** conexión SSH (llave/agent primero, contraseña como respaldo).
3. Crea la carpeta remota si no existe, sube el archivo y le pone permisos `644`.
4. Copia la ruta remota (`/tmp/screenshots/screenshot-AAAAMMDD-HHMMSS.png`) al portapapeles.

## Requisitos

- Windows 10/11
- Python 3.9 o superior
- Acceso SSH al servidor (llave o contraseña)

## Instalación

Desde la carpeta del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install paramiko pillow pyperclip python-dotenv
```

Si ya tienes un `requirements.txt`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

> Se usa un entorno virtual (`.venv`) para que las dependencias queden dentro del proyecto y no se instalen en el Python global ni en el de tu usuario. No hace falta "activarlo": basta con llamar directamente al `python.exe` del venv.

## Configuración

Crea un archivo `.env` en la **misma carpeta que el script**:

```env
SSH_HOST=tu.servidor.o.ip
SSH_USER=tu_usuario
SSH_PASSWORD=tu_password
REMOTE_DIR=/tmp/screenshots
```

| Variable | Obligatoria | Descripción |
| --- | --- | --- |
| `SSH_HOST` | Sí | IP o dominio del servidor |
| `SSH_USER` | Sí | Usuario SSH |
| `SSH_PASSWORD` | No | Contraseña. Si no la defines y no hay llave, el script la pide por teclado |
| `REMOTE_DIR` | No | Carpeta remota donde se guardan las capturas (por defecto `/tmp/screenshots`) |

## Uso

1. Copia una imagen al portapapeles (`Win+Shift+S` o cualquier captura).
2. Ejecuta el script:

   ```powershell
   .\.venv\Scripts\python.exe .\paste_image_ssh.py
   ```

3. Verás algo como `Listo: /tmp/screenshots/screenshot-20261001-153000.png`.
4. Ve a tu sesión SSH/tmux y pega la ruta con `Ctrl+Shift+V` (o clic derecho, según tu terminal).

## Autenticación

El script intenta autenticarse en este orden:

1. **Llave SSH / ssh-agent** (si existe)
2. **Contraseña** del `.env` (`SSH_PASSWORD`)
3. **Contraseña por teclado** (si no está en el `.env`)

### Recomendado: usar llave SSH (sin contraseñas)

```powershell
# Generar la llave (si no tienes una)
ssh-keygen -t ed25519

# Copiar la llave pública al servidor (pedirá la contraseña una última vez)
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh usuario@servidor "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

Después de esto ya no necesitas `SSH_PASSWORD` en el `.env`. Una vez que la llave funcione, conviene desactivar el login por contraseña en el servidor (`PasswordAuthentication no` en `/etc/ssh/sshd_config`).

## Extra: alias de PowerShell

Para no escribir la ruta completa cada vez, puedes crear un comando corto (`pimg`).

1. Crea tu perfil de PowerShell si no existe y ábrelo:

   ```powershell
   New-Item -Path $PROFILE -ItemType File -Force
   notepad $PROFILE
   ```

2. Agrega esta función (ajusta la ruta a donde tengas el proyecto):

   ```powershell
   function pimg {
       C:\ruta\al\proyecto\.venv\Scripts\python.exe C:\ruta\al\proyecto\paste_image_ssh.py
   }
   ```

3. Guarda, y recarga el perfil:

   ```powershell
   . $PROFILE
   ```

Ahora basta con copiar una captura y escribir:

```powershell
pimg
```

Si PowerShell te dice que la ejecución de scripts está deshabilitada, corre una vez:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

## Extra: atajo de teclado global (AutoHotkey v2)

Si prefieres no abrir una terminal, con [AutoHotkey v2](https://www.autohotkey.com/) puedes lanzar el script con un atajo (por ejemplo `Ctrl+Alt+V`):

```ahk
^!v::Run '"C:\ruta\al\proyecto\.venv\Scripts\pythonw.exe" "C:\ruta\al\proyecto\paste_image_ssh.py"'
```

`pythonw.exe` no muestra consola, así que:

- Los errores no se ven en pantalla.
- No puede pedir la contraseña por teclado: debes tener llave SSH o `SSH_PASSWORD` en el `.env`.

## Solución de problemas

| Problema | Causa / solución |
| --- | --- |
| `ModuleNotFoundError` | Estás usando el `python` global en vez del del venv. Usa `.\.venv\Scripts\python.exe` |
| `KeyError: 'SSH_HOST'` | Falta el `.env` o no está junto al script, o la variable no está definida |
| `No hay ninguna imagen en el portapapeles` | Copiaste un archivo o texto en vez de una imagen. Haz una captura con `Win+Shift+S` |
| `AuthenticationException` | Usuario o contraseña incorrectos, o el servidor no acepta login por contraseña |
| `python` no se reconoce | Prueba con `py` o revisa que Python esté en el `PATH` |
| El atajo de AutoHotkey no hace nada | Revisa la ruta de `pythonw.exe` y prueba el script primero con `python.exe` para ver los errores |
| El venv dejó de funcionar tras mover la carpeta | Los venv guardan rutas absolutas. Bórralo y recréalo con los pasos de instalación |

## Notas

- `AutoAddPolicy` acepta automáticamente la host key del servidor la primera vez. Para mayor seguridad, conéctate una vez con `ssh usuario@servidor` para registrarla en `known_hosts` y cambia la política a `RejectPolicy` en el script.
- Las capturas quedan en `REMOTE_DIR` del servidor. Si usas `/tmp`, se limpian solas con el tiempo o al reiniciar.