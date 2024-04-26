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
import zipfile

models.Base.metadata.create_all(bind=engine)

# /users/
PARENT_MEDIA_NAME = config_sething.parent_media_name
MEDIA_PATHS = {
    "user_medias": "user_medias",# pour la photo de profile du user
    "categorie_articles_medias": "categorie_articles_medias",# photo des produit
    "articles_medias": "articles_medias",
    
    
}
router = APIRouter(prefix = "/medias", tags=['Medias Requests'])

 
 
@router.post("/uploadfiles/")
async def create_upload_files(media_use: str = None, files: List[UploadFile] = File(...)):
    
    """Using this API, you can organise files in designated
    directories, verify file extensions, and download and 
    save multimedia assets (videos and photos) on a server."""
    
    if media_use not in MEDIA_PATHS:
        raise HTTPException(status_code=404, detail=f"We don't have this media files!")

    if not os.path.exists(PARENT_MEDIA_NAME):
        os.makedirs(PARENT_MEDIA_NAME)

    # Vérifier si le répertoire enfant existe
    child_path = os.path.join(PARENT_MEDIA_NAME, MEDIA_PATHS[media_use])
    if not os.path.exists(child_path):
        os.makedirs(child_path)

    media_names = []
    for file in files:
        try:
            # Enregistrer les vidéos avec un nom différent
            if file.filename.endswith(".mp4"):
                filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f") + "_" + file.filename
                with open(os.path.join(child_path, filename), "wb") as video_file:
                    video_file.write(file.file.read())
                media_names.append(filename)
            else:
                image = Image.open(file.file)
                filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f") + "_" + file.filename
                image.save(os.path.join(child_path, filename))
                media_names.append(filename)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save media: {str(e)}")

    return {"media_information": media_names}


@router.get("/medias/")
async def get_media_files(media_use: str, image_names: List[str] = Form(...)):
    """The API obtains each media item and returns it as a list
    of file replies when you supply a list of media names.
    A 404 error message will appear if the media that was requested cannot be located."""
    
    if media_use not in MEDIA_PATHS:
        raise HTTPException(status_code=404, detail=f"We don't have this media files!")

    if not os.path.exists(PARENT_MEDIA_NAME):
        os.makedirs(PARENT_MEDIA_NAME)

    # Vérifier si le répertoire enfant existe
    child_path = os.path.join(PARENT_MEDIA_NAME, MEDIA_PATHS[media_use])
    if not os.path.exists(child_path):
        raise HTTPException(status_code=404, detail=f"Media files not found!")

    zip_filename = f"{media_use}_files.zip"
    with zipfile.ZipFile(zip_filename, "w") as zipf:
        for image_name in image_names:
            image_path = os.path.join(child_path, image_name)
            if not os.path.exists(image_path):
                raise HTTPException(status_code=404, detail=f"Media file '{image_name}' not found!")
            zipf.write(image_path, arcname=image_name)

    return FileResponse(zip_filename, media_type="application/zip", filename=zip_filename)
 
  
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
   
# #     return responses
# @router.post("/upload_file/")
# async def upload_file(file: UploadFile = File(...), media_use: str = None):
    
#     if media_use not in MEDIA_PATHS:
#         raise HTTPException(status_code=403, detail="This file cannot be saved, sorry!")

#     if not os.path.exists(PARENT_MEDIA_NAME):
#         os.makedirs(PARENT_MEDIA_NAME)

#     # Vérifier si le répertoire enfant existe
#     child_path = os.path.join(PARENT_MEDIA_NAME, media_use)
#     if not os.path.exists(child_path):
#         os.makedirs(child_path)

#     file.filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f") + "_" + file.filename
    
#     file_path = os.path.join(child_path, file.filename)
#     with open(file_path, "wb") as video_file:
#         video_file.write(file.file.read())

#     return file.filename

# @router.get("/get_file/{video_file:str},{media_use:str}")
# async def get_files(video_file: str, media_use: str):

#     if media_use not in MEDIA_PATHS:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"We don't have media files for this media type!")
    
#     if not os.path.exists(PARENT_MEDIA_NAME):
#         os.makedirs(PARENT_MEDIA_NAME)

#     # Vérifier si le répertoire enfant existe
#     child_path = os.path.join(PARENT_MEDIA_NAME, media_use)
#     if not os.path.exists(child_path):
#         os.makedirs(child_path)
        
#     child_path = os.path.join(PARENT_MEDIA_NAME, media_use)
#     video_path = os.path.join(child_path, video_file)

#     if os.path.exists(video_path):
#         return FileResponse(video_path)
      
#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")


# # delet media
# async def delete_media(media_delet: str, media_use: str):
#     """
#     Endpoint pour supprimer un fichier média.

#     Parameters:
#     - `media_delet`: Le nom du fichier média dans le système de fichiers.

#     Returns:
#     - Message indiquant si la suppression a réussi ou non.
#     """
#     if media_use not in MEDIA_PATHS:
#         raise HTTPException(status_code=404, detail=f"We don't have this media files!")
    
#     try:
#         # Construction du chemin complet du fichier média
#         full_path = os.path.join(PARENT_MEDIA_NAME, media_use, media_delet)

#         # Vérifier si le fichier existe
#         if os.path.exists(full_path):
#             # Supprimer le fichier
#             os.remove(full_path)
#             return {"message": f"Le fichier {media_delet} a été supprimé avec succès."}
#         else:
#             raise HTTPException(status_code=404, detail=f"Le fichier {media_delet} n'a pas été trouvé.")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Une erreur s'est produite lors de la suppression du fichier : {str(e)}")

