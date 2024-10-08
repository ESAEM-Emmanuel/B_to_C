import os
from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
from datetime import datetime
from PIL import Image
from app import config_sething  # Importer les configurations serveur

# Définir le répertoire unique pour les fichiers médias
MEDIA_PATHS = "medias"

# Assurez-vous que le répertoire des médias existe
if not os.path.exists(MEDIA_PATHS):
    os.makedirs(MEDIA_PATHS)

router = APIRouter(prefix="/medias", tags=['Medias Requests'])

# Configuration de la route statique pour accéder aux fichiers médias


router.mount("/medias", StaticFiles(directory=MEDIA_PATHS), name="medias")
@router.post("/uploadfiles/")
async def create_upload_files(files: List[UploadFile] = File(...)):
    """Upload des fichiers médias et retour d'une liste d'URLs accessibles."""
    if not os.path.exists(MEDIA_PATHS):
        os.makedirs(MEDIA_PATHS)

    media_urls = []
    for file in files:
        try:
            # Enregistrer les vidéos ou images
            if file.filename.endswith(".mp4"):
                filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f") + "_" + file.filename
                with open(os.path.join(MEDIA_PATHS, filename), "wb") as video_file:
                    video_file.write(file.file.read())
            else:
                image = Image.open(file.file)
                filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f") + "_" + file.filename
                image.save(os.path.join(MEDIA_PATHS, filename))

            # Générer l'URL publique dynamique avec host et port depuis config_sething
            file_url = f"http://{config_sething.server_host}:{config_sething.server_port}/static/{filename}"
            media_urls.append(file_url)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save media: {str(e)}")

    return {"media_urls": media_urls}
