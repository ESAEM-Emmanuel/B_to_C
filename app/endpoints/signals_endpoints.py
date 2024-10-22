import os
from fastapi import APIRouter, HTTPException, Depends, status, Request, File, UploadFile
from sqlalchemy import desc
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app.schemas import signals_schemas
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from app.models import models
import uuid
from datetime import datetime, timedelta
from app.database import engine, get_db
from typing import Optional
from  utils import oauth2
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from math import ceil

models.Base.metadata.create_all(bind=engine)

# Fonction pour permuter la valeur d'un booléen
def toggle_boolean(value):
    return not value

# /signals/

router = APIRouter(prefix = "/signal", tags=['Signals Requests'])
 
# create signal or dissignal
@router.post("/create/", status_code = status.HTTP_201_CREATED, response_model=signals_schemas.SignalListing)
async def create_signal(new_signal_c: signals_schemas.SignalCreate, db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
    author = current_user.id
    if new_signal_c.article_id :
        signals_queries = db.query(models.Signal).filter(models.Signal.owner_id == author, models.Signal.article_id == new_signal_c.article_id ).first()
    
    if not signals_queries:
        
        formated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")# Formatage de la date au format souhaité (par exemple, YYYY-MM-DD HH:MM:SS)
        concatenated_uuid = str(uuid.uuid4())#+ ":" + formated_date
        NUM_REF = 10001
        codefin = datetime.now().strftime("%m/%Y")
        concatenated_num_ref = str(
                NUM_REF + len(db.query(models.Signal).filter(models.Signal.refnumber.endswith(codefin)).all())) + "/" + codefin
        
        signals_queries= models.Signal(id = concatenated_uuid, **new_signal_c.dict(), refnumber = concatenated_num_ref, owner_id = author)
        
        try:
            db.add(signals_queries )# pour ajouter une tuple
            db.commit() # pour faire l'enregistrement
            db.refresh(signals_queries)# pour renvoyer le résultat
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
        
    else:
        
        signals_queries.active = toggle_boolean(signals_queries.active)
        try:
            db.add(signals_queries )# pour ajouter une tuple
            db.commit() # pour faire l'enregistrement
            db.refresh(signals_queries)# pour renvoyer le résultat
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=403, detail="Somthing is wrong in the process, we can't validated your signal!")
    
    return jsonable_encoder(signals_queries)

# Get all signals requests
@router.get("/")
async def get_all_signals(skip: int = 0, limit: int = 100, active: Optional[bool] = None, db: Session = Depends(get_db)):
    try:
        query = db.query(models.Signal)

        # Filtrer par actif/inactif si fourni
        if active is not None:
            query = query.filter(models.Signal.active == active)
            
        if limit ==-1:
            query = query.filter(models.Signal.active == active)
            serialized_signals = [signals_schemas.SignalListing.from_orm(signal) for signal in signals]
            return {
                "signals": jsonable_encoder(serialized_signals)
            }

        total_signals = query.count()  # Nombre total de pays

        # Pagination
        signals = query.order_by(desc(models.Signal.created_at)).offset(skip).limit(limit).all()

        total_pages = ceil(total_signals / limit) if limit > 0 else 1
        
        serialized_signals = []
        for signal in signals:
            # serialized_countrie = [signals_schemas.SignalListing.from_orm(signal) for signal in signals]
            serialized_signal = signals_schemas.SignalListing.from_orm(signal)
            if signal.owner_id :
                # Récupération des détails du pays
                owner_query = db.query(models.User).filter(models.User.id == signal.owner_id).first()
                if not owner_query:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"signal with id: {signal.created_by} does not exist")
                owner_serialized = signals_schemas.UserInfo.from_orm(owner_query)
                serialized_signal.owner = owner_serialized
            if signal.article_id :
                # Récupération des détails du pays
                article_query = db.query(models.Article).filter(models.Article.id == signal.article_id).first()
                if not article_query:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"article with id: {signal.article_id} does not exist")
                article_serialized = signals_schemas.ArticleList.from_orm(article_query)
                serialized_signal.article = article_serialized
            if signal.updated_by:
                updator_query = db.query(models.User).filter(models.User.id == signal.updated_by).first()
                if not updator_query:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"signal with id: {signal.updated_by} does not exist")
                updator_serialized = signals_schemas.UserInfo.from_orm(updator_query)  # Use updator_query here
                serialized_signal.updator = updator_serialized
            serialized_signals.append(serialized_signal)

        return {
            "signals": jsonable_encoder(serialized_signals),
            "total_signals": total_signals,
            "total_pages": total_pages,
            "current_page": (skip // limit) + 1 if limit > 0 else 1
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    

@router.get("/search/")
async def search_countries(
    refnumber: Optional[str] = None,
    article_id: Optional[str] = None,
    owner_id: Optional[str] = None,
    description: Optional[str] = None,
    active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        query = db.query(models.Signal)

        # Filtrer par nom si fourni
        if refnumber:
            query = query.filter(models.Signal.refnumber.contains(refnumber))
        if article_id:
            query = query.filter(models.Signal.article_id.contains(article_id))
        if owner_id:
            query = query.filter(models.Signal.owner_id.contains(owner_id))
        if description:
            query = query.filter(models.Signal.description.contains(description.lower()))
        # Filtrer par statut actif/inactif
        if active is not None:
            query = query.filter(models.Country.active == active)
        
        total_signals = query.count()  # Nombre total de pays

        # Pagination
        signals = query.order_by(desc(models.Signal.created_at)).offset(skip).limit(limit).all()

        total_pages = ceil(total_signals / limit) if limit > 0 else 1
        
        serialized_signals = []
        for signal in signals:
            # serialized_countrie = [signals_schemas.SignalListing.from_orm(signal) for signal in signals]
            serialized_signal = signals_schemas.SignalListing.from_orm(signal)
            if signal.owner_id :
                # Récupération des détails du pays
                owner_query = db.query(models.User).filter(models.User.id == signal.owner_id).first()
                if not owner_query:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"signal with id: {signal.created_by} does not exist")
                owner_serialized = signals_schemas.UserInfo.from_orm(owner_query)
                serialized_signal.owner = owner_serialized
            if signal.article_id :
                # Récupération des détails du pays
                article_query = db.query(models.Article).filter(models.Article.id == signal.article_id).first()
                if not article_query:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"article with id: {signal.article_id} does not exist")
                article_serialized = signals_schemas.ArticleList.from_orm(article_query)
                serialized_signal.article = article_serialized
            if signal.updated_by:
                updator_query = db.query(models.User).filter(models.User.id == signal.updated_by).first()
                if not updator_query:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"signal with id: {signal.updated_by} does not exist")
                updator_serialized = signals_schemas.UserInfo.from_orm(updator_query)  # Use updator_query here
                serialized_signal.updator = updator_serialized
            serialized_signals.append(serialized_signal)

        return {
            "signals": jsonable_encoder(serialized_signals),
            "total_signals": total_signals,
            "total_pages": total_pages,
            "current_page": (skip // limit) + 1 if limit > 0 else 1
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# Get an signal
@router.get("/get/{signal_id}", status_code=status.HTTP_200_OK, response_model=signals_schemas.SignalDetail)
async def detail_signal(signal_id: str, db: Session = Depends(get_db)):
    query = db.query(models.Signal).filter(models.Signal.id == signal_id).first()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"signal with id: {signal_id} does not exist")
    
    # serialized_countrie = [signals_schemas.SignalListing.from_orm(signal) for signal in signals]
    serialized_signal = signals_schemas.SignalDetail.from_orm(query)
    if query.owner_id :
        # Récupération des détails du pays
        owner_query = db.query(models.User).filter(models.User.id == query.owner_id).first()
        if not owner_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"signal with id: {query.created_by} does not exist")
        owner_serialized = signals_schemas.UserInfo.from_orm(owner_query)
        serialized_signal.owner = owner_serialized
    if query.article_id :
        # Récupération des détails du pays
        article_query = db.query(models.Article).filter(models.Article.id == query.article_id).first()
        if not article_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"article with id: {query.article_id} does not exist")
        article_serialized = signals_schemas.ArticleList.from_orm(article_query)
        serialized_signal.article = article_serialized
    if query.updated_by:
        updator_query = db.query(models.User).filter(models.User.id == query.updated_by).first()
        if not updator_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"signal with id: {query.updated_by} does not exist")
        updator_serialized = signals_schemas.UserInfo.from_orm(updator_query)  # Use updator_query here
        serialized_signal.updator = updator_serialized
        
    return jsonable_encoder(serialized_signal)






