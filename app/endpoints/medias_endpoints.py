import os
from fastapi import APIRouter, HTTPException, Depends, status, Request, File, UploadFile,Form
from app.models import models
from app import config_sething
from app.database import engine, get_db
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from typing import List
from datetime import datetime
from PIL import Image
# from multipart.multipart import parse_options_header

models.Base.metadata.create_all(bind=engine)

# /users/
PARENT_MEDIA_NAME = config_sething.parent_media_name
MEDIA_PATHS = {
    "user_medias": "user_medias",# pour la photo de profile du user
    "categorie_articles_medias": "categorie_articles_medias",# photo des produit
    "articles_medias": "articles_medias",
    
    
}
router = APIRouter(prefix = "/medias", tags=['Medias Requests'])

    
#     return responses
@router.post("/upload_file/")
async def upload_file(file: UploadFile = File(...), media_use: str = None):
    
    if media_use not in MEDIA_PATHS:
        raise HTTPException(status_code=403, detail="This file cannot be saved, sorry!")

    if not os.path.exists(PARENT_MEDIA_NAME):
        os.makedirs(PARENT_MEDIA_NAME)

    # Vérifier si le répertoire enfant existe
    child_path = os.path.join(PARENT_MEDIA_NAME, media_use)
    if not os.path.exists(child_path):
        os.makedirs(child_path)

    file.filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f") + "_" + file.filename
    
    file_path = os.path.join(child_path, file.filename)
    with open(file_path, "wb") as video_file:
        video_file.write(file.file.read())

    return file.filename

@router.get("/get_file/{video_file:str},{media_use:str}")
async def get_files(video_file: str, media_use: str):

    if media_use not in MEDIA_PATHS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"We don't have media files for this media type!")
    
    if not os.path.exists(PARENT_MEDIA_NAME):
        os.makedirs(PARENT_MEDIA_NAME)

    # Vérifier si le répertoire enfant existe
    child_path = os.path.join(PARENT_MEDIA_NAME, media_use)
    if not os.path.exists(child_path):
        os.makedirs(child_path)
        
    child_path = os.path.join(PARENT_MEDIA_NAME, media_use)
    video_path = os.path.join(child_path, video_file)

    if os.path.exists(video_path):
        return FileResponse(video_path)
      
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")


# delet media
async def delete_media(media_delet: str, media_use: str):
    """
    Endpoint pour supprimer un fichier média.

    Parameters:
    - `media_delet`: Le nom du fichier média dans le système de fichiers.

    Returns:
    - Message indiquant si la suppression a réussi ou non.
    """
    if media_use not in MEDIA_PATHS:
        raise HTTPException(status_code=404, detail=f"We don't have this media files!")
    
    try:
        # Construction du chemin complet du fichier média
        full_path = os.path.join(PARENT_MEDIA_NAME, media_use, media_delet)

        # Vérifier si le fichier existe
        if os.path.exists(full_path):
            # Supprimer le fichier
            os.remove(full_path)
            return {"message": f"Le fichier {media_delet} a été supprimé avec succès."}
        else:
            raise HTTPException(status_code=404, detail=f"Le fichier {media_delet} n'a pas été trouvé.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Une erreur s'est produite lors de la suppression du fichier : {str(e)}")

