import os
from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.staticfiles import StaticFiles
from typing import List
from datetime import datetime
from PIL import Image
from app.config import settings  # Importez les configurations depuis settings

# Définir le répertoire unique pour les fichiers médias
MEDIA_PATHS = settings.PARENT_MEDIA_NAME

# Assurez-vous que le répertoire des médias existe
if not os.path.exists(MEDIA_PATHS):
    os.makedirs(MEDIA_PATHS)

router = APIRouter(prefix="/medias", tags=['Medias Requests'])

# Configuration de la route statique pour accéder aux fichiers médias
router.mount("/static", StaticFiles(directory=MEDIA_PATHS), name="static")

@router.post("/uploadfiles/")
async def create_upload_files(files: List[UploadFile] = File(...)):
    """Upload des fichiers médias et retour d'une liste d'URLs accessibles."""
    if not os.path.exists(MEDIA_PATHS):
        os.makedirs(MEDIA_PATHS)

    media_urls = []
    for file in files:
        try:
            # Générer un nom de fichier unique basé sur la date et l'heure
            filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f") + "_" + file.filename

            # Enregistrer les vidéos ou images
            file_path = os.path.join(MEDIA_PATHS, filename)
            if file.filename.endswith(".mp4"):
                with open(file_path, "wb") as video_file:
                    video_file.write(file.file.read())
            else:
                image = Image.open(file.file)
                image.save(file_path)

            # Générer l'URL publique dynamique avec host et port depuis settings
            file_url = f"http://{settings.HOST}:{settings.PORT}/static/{filename}"
            media_urls.append(file_url)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save media: {str(e)}")

    return {"media_urls": media_urls}