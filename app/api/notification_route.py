from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.schemas.notifications_schemas import (
    NotificationCreate,
    NotificationUpdate,
    NotificationSchema,)
from app.schemas.utils_schemas import (PaginatedResponse,
PaginationMetadata,
ArticleSchema,
UserInfo,
)
from app.database import get_db
from typing import Optional, List
from datetime import date, datetime, time
from app.crud.notification_crud import (
    research,
    create,
    get_by_id,
    update,
    delete,
    restore,
)
from app.utils.utils import verify,get_user_by_id
from app.crud.auth_crud import (get_user_from_token_optional,
get_user_from_token)

router = APIRouter(prefix="/notifications", tags=["Notifications Requests"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=NotificationSchema)
async def create_route(
    item: NotificationCreate, 
    db: Session = Depends(get_db), 
    current_user: Optional[str] = Depends(get_user_from_token)
):
    try:
        item = create(db, item, current_user.id if current_user else None)
        # Récupération du créateur
        creator = get_user_by_id(db, item.created_by) if item.created_by else None
        updator = get_user_by_id(db, item.updated_by) if item.updated_by else None

        # Retourne le PrivilegeUser avec le créateur sérialisé
        return NotificationSchema.from_orm(item).copy(update={
            "creator": creator,
            "updator": updator}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=PaginatedResponse[NotificationSchema])
async def get_signals(
    article_id: Optional[str] = Query(None, description="Filtrer par ID de l'article"),
    description: Optional[str] = Query(None, description="Filtrer par description (recherche partielle)"),
    refnumber: Optional[str] = Query(None, description="Filtrer par numéro de référence (recherche partielle)"),
    created_by: Optional[str] = Query(None, description="Filtrer par utilisateur ayant créé le signalement"),
    created_at: Optional[date] = Query(None, description="Filtrer par date de création (exacte ou plage)"),
    created_at_bis: Optional[date] = Query(None, description="Date de fin pour la plage de création"),
    created_at_operation: Optional[str] = Query(None, description="Opération sur la date de création ('inf', 'sup')"),
    updated_by: Optional[str] = Query(None, description="Filtrer par utilisateur ayant mis à jour le signalement"),
    updated_at: Optional[date] = Query(None, description="Filtrer par date de mise à jour (exacte ou plage)"),
    updated_at_bis: Optional[date] = Query(None, description="Date de fin pour la plage de mise à jour"),
    updated_at_operation: Optional[str] = Query(None, description="Opération sur la date de mise à jour ('inf', 'sup')"),
    is_read: Optional[bool] = Query(None, description="Filtrer par statut lu/non lu"),
    active: Optional[bool] = Query(None, description="Filtrer par statut actif/inactif"),
    order: str = Query("asc", description="Ordre de tri ('asc' ou 'desc')"),
    sort_by: str = Query("created_at", description="Colonne utilisée pour le tri"),
    skip: int = Query(0, ge=0, description="Nombre d'enregistrements à ignorer pour la pagination"),
    limit: int = Query(100, ge=-1, description="Nombre maximal d'enregistrements à renvoyer (-1 pour tous les actifs)"),
    db: Session = Depends(get_db),
):
    """
    Récupère une liste paginée et filtrée de signalements.
    """
    # Appel à la fonction de recherche
    items, total_records = research(
        db=db,
        article_id=article_id,
        description=description,
        is_read=is_read,
        refnumber=refnumber,
        created_by=created_by,
        created_at=created_at,
        created_at_bis=created_at_bis,
        created_at_operation=created_at_operation,
        updated_by=updated_by,
        updated_at=updated_at,
        updated_at_bis=updated_at_bis,
        updated_at_operation=updated_at_operation,
        active=active,
        order=order,
        sort_by=sort_by,
        skip=skip,
        limit=limit,
    )

    # Calcul du nombre total de pages
    if limit == -1:
        total_pages = 1  # Tous les signalements actifs sont renvoyés
        current_page = 1
    else:
        total_pages = (total_records // limit) + 1 if limit > 0 else 1
        current_page = (skip // limit) + 1 if limit > 0 else 1

    # Transformation des objets SQLAlchemy en instances Pydantic
    serialized = [
        NotificationSchema(
            id=item.id,
            article_id=item.article_id,
            description=item.description,
            is_read=item.is_read,
            refnumber=item.refnumber,
            created_at=item.created_at,
            updated_at=item.updated_at,
            active=item.active,
            article=ArticleSchema.model_validate(item.article) if item.article else None,  # Transforme la relation article en ArticleSchema
            creator=get_user_by_id(db, item.created_by) if item.created_by else None,
            updator=get_user_by_id(db, item.updated_by) if item.updated_by else None
        )
        for item in items
    ]

    # Construction de la réponse paginée
    return PaginatedResponse[NotificationSchema](
        records=serialized,
        metadata=PaginationMetadata(
            total_records=total_records,
            total_pages=total_pages,
            current_page=current_page,
        ),
    )

@router.get("/{id}", response_model=NotificationSchema)
async def get_detail(id: str, db: Session = Depends(get_db)):
    item = get_by_id(db, id)
    if not item:
        raise HTTPException(status_code=404, detail="Signal not found.")
    # Récupération du créateur
    creator = get_user_by_id(db, item.created_by) if item.created_by else None
    updator = get_user_by_id(db, item.updated_by) if item.updated_by else None

    # Retourne le PrivilegeUser avec le créateur sérialisé
    return NotificationSchema.from_orm(item).copy(update={
        "creator": creator,
        "updator": updator}
    )

@router.put("/{id}", response_model=NotificationSchema)
async def update_route(
    id: str, 
    n_update: NotificationUpdate, 
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_user_from_token)
):
    try:
        item = update(db, id, n_update, current_user.id)
        # Récupération du créateur
        creator = get_user_by_id(db, item.created_by) if item.created_by else None
        updator = get_user_by_id(db, item.updated_by) if item.updated_by else None

        # Retourne le roleavec le créateur sérialisé
        return NotificationSchema.from_orm(item).copy(update={
            "creator": creator,
            "updator": updator}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_route(
    id: str, 
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_user_from_token)
):
    try:
        delete(db, id, current_user.id)
        return {"message": "User deleted!"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/restore/{id}", response_model=NotificationSchema)
async def restore_route(
    id: str, 
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_user_from_token)
):
    try:
        item = restore(db, id, current_user.id)
        # Récupération du créateur
        creator = get_user_by_id(db, item.created_by) if item.created_by else None
        updator = get_user_by_id(db, item.updated_by) if item.updated_by else None

        # Retourne le roleavec le créateur sérialisé
        return NotificationSchema.from_orm(item).copy(update={
            "creator": creator,
            "updator": updator}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))