from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.schemas.subscription_types_schemas import (
    SubscriptionTypeCreate,
    SubscriptionTypeUpdate,
    SubscriptionTypeSchema,)
from app.schemas.utils_schemas import (PaginatedResponse, PaginationMetadata)
from app.database import get_db
from typing import Optional, List
from datetime import date, datetime, time
from app.models.models import StatusProposition
from app.crud.subscription_type_crud import (
    research,
    create,
    update,
    delete,
    get_by_id,
    restore,
)
from app.utils.utils import verify,get_user_by_id

from app.crud.auth_crud import (get_user_from_token_optional,
get_user_from_token)
router = APIRouter(prefix="/subscription_types", tags=["Subscription Types Requests"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SubscriptionTypeSchema)
async def create_route(
    item: SubscriptionTypeCreate, 
    db: Session = Depends(get_db), 
    current_user: Optional[str] = Depends(get_user_from_token)
):
    try:
        item = create(db, item, current_user.id if current_user else None)
        # Récupération du créateur
        creator = get_user_by_id(db, item.created_by) if item.created_by else None
        updator = get_user_by_id(db, item.updated_by) if item.updated_by else None

        # Retourne le SubscriptionTypeavec le créateur sérialisé
        return SubscriptionTypeSchema.from_orm(item).copy(update={
            "creator": creator,
            "updator": updator}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.get("/", response_model=PaginatedResponse[SubscriptionTypeSchema])
async def research_route(
    name: Optional[str] = Query(None),
    advertisements: Optional[int] = Query(None),
    advertisements_bis: Optional[int] = Query(None),
    advertisements_operation: Optional[str] = Query(None),
    price: Optional[float] = Query(None),
    price_bis: Optional[float] = Query(None),
    price_operation: Optional[str] = Query(None),
    price_max_article: Optional[float] = Query(None),
    price_max_article_bis: Optional[float] = Query(None),
    price_max_article_operation: Optional[str] = Query(None),
    duration: Optional[int] = Query(None),
    duration_bis: Optional[int] = Query(None),
    duration_operation: Optional[str] = Query(None),
    status: Optional[StatusProposition] = Query(None),
    refnumber: Optional[str] = Query(None),
    created_by: Optional[str] = Query(None),
    created_at: Optional[date] = Query(None),
    created_at_bis: Optional[date] = Query(None),
    created_at_operation: Optional[str] = Query(None),
    updated_by: Optional[str] = Query(None),
    updated_at: Optional[date] = Query(None),
    updated_at_bis: Optional[date] = Query(None),
    updated_at_operation: Optional[str] = Query(None),
    active: Optional[bool] = Query(None),
    order: str = "asc",
    sort_by: str = "name",
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    # Conversion explicite de status (facultatif)
    if status:
        try:
            status = StatusProposition(status.value)  # Convertir explicitement
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status value: {status}. Valid options are: {[e.value for e in StatusProposition]}"
            )

    # Appel à la fonction de recherche
    items, total_records = research(
        db=db,
        name=name,
        advertisements=advertisements,
        advertisements_bis=advertisements_bis,
        advertisements_operation=advertisements_operation,
        price=price,
        price_bis=price_bis,
        price_operation=price_operation,
        price_max_article=price_max_article,
        price_max_article_bis=price_max_article_bis,
        price_max_article_operation=price_max_article_operation,
        duration=duration,
        duration_bis=duration_bis,
        duration_operation=duration_operation,
        status=status,
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
        total_pages = 1  # Tous les utilisateurs actifs sont renvoyés
        current_page = 1
    else:
        total_pages = (total_records // limit) + 1 if limit > 0 else 1
        current_page = (skip // limit) + 1 if limit > 0 else 1

    serialized = [
        SubscriptionTypeSchema(
            **item.__dict__,  # Sérialise l'objet principal
            creator=get_user_by_id(db, item.created_by) if item.created_by else None,
            updator=get_user_by_id(db, item.updated_by) if item.updated_by else None
        )
        for item in items
    ]

    # Construction de la réponse paginée
    return PaginatedResponse[SubscriptionTypeSchema](
        records=serialized,
        metadata=PaginationMetadata(
            total_records=total_records,
            total_pages=total_pages,
            current_page=current_page,
        ),
    )

@router.get("/{id}", response_model=SubscriptionTypeSchema)
async def get_detail(id: str, db: Session = Depends(get_db)):
    item = get_by_id(db, id)
    if not item:
        raise HTTPException(status_code=404, detail="User not found.")
    # Récupération du créateur
    creator = get_user_by_id(db, item.created_by) if item.created_by else None
    updator = get_user_by_id(db, item.updated_by) if item.updated_by else None

    # Retourne le SubscriptionTypeavec le créateur sérialisé
    return SubscriptionTypeSchema.from_orm(item).copy(update={
        "creator": creator,
        "updator": updator}
    )


@router.put("/{id}", response_model=SubscriptionTypeSchema)
async def update_route(
    id: str, 
    n_update: SubscriptionTypeUpdate, 
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_user_from_token)
):
    try:
        item = update(db, id, n_update, current_user.id)
        # Récupération du créateur
        creator = get_user_by_id(db, item.created_by) if item.created_by else None
        updator = get_user_by_id(db, item.updated_by) if item.updated_by else None

        # Retourne le SubscriptionTypeavec le créateur sérialisé
        return SubscriptionTypeSchema.from_orm(item).copy(update={
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

@router.patch("/restore/{id}", response_model=SubscriptionTypeSchema)
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

        # Retourne le SubscriptionTypeavec le créateur sérialisé
        return SubscriptionTypeSchema.from_orm(item).copy(update={
            "creator": creator,
            "updator": updator}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))