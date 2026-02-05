# video-download-v3

API FastAPI para extraer imágenes y la URL directa de video de posts públicos de Facebook usando Selenium.

Esta versión intenta desplegar en Render sin usar Docker — el repositorio contiene un `Procfile` y un script `start.sh` que intentará instalar un chromedriver compatible en el arranque.

Instalación local:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Ejecutar localmente:

```powershell
py -3 -m uvicorn main_selenium:app --reload --host 127.0.0.1 --port 8001
```

En Render (sin Docker):

- Asegúrate de que el servicio use `Python` como runtime.
- `Build Command`: `pip install -r requirements.txt`
- `Start Command`: `sh start.sh` (o `uvicorn main_selenium:app --host 0.0.0.0 --port $PORT` si no quieres que el script instale chromedriver automáticamente).

Endoints principales: idem v2.
