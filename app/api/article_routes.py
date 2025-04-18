from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.schemas.articles_schemas import (
    ArticleCreate,
    ArticleUpdate,
    ArticleSchema,)
from app.schemas.utils_schemas import (PaginatedResponse, PaginationMetadata)
from app.database import get_db
from typing import Optional, List
from datetime import date, datetime, time
from app.models.models import StatusArticle
from app.crud.article_crud import (
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
router = APIRouter(prefix="/articles", tags=["Articles Requests"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ArticleSchema)
async def create_route(
    item: ArticleCreate, 
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_user_from_token)
):
    try:
        item = create(db, item, current_user.id if current_user else None)
        # Récupération du créateur
        owner=item.owner if item.owner else None,  # Inclure explicitement la relation town
        subscription=item.subscription if item.subscription else None,  # Inclure explicitement la relation town
        town=item.town if item.town else None,  # Inclure explicitement la relation town
        creator=get_user_by_id(db, item.created_by) if item.created_by else None,
        updator=get_user_by_id(db, item.updated_by) if item.updated_by else None

        # Retourne l'utilisateur avec le créateur sérialisé
        return ArticleSchema.from_orm(item).copy(update={
            "creator": creator,
            "updator": updator}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=PaginatedResponse[ArticleSchema])  # Spécifiez ArticleSchema ici
async def research_route(
    name: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    reception_place: Optional[str] = Query(None),
    phone: Optional[str] = Query(None),
    phone_transaction: Optional[str] = Query(None),
    price: Optional[float] = Query(None),
    price_bis: Optional[float] = Query(None),
    price_operation: Optional[str] = Query(None),
    nb_visite: Optional[float] = Query(None),
    nb_visite_bis: Optional[float] = Query(None),
    nb_visite_operation: Optional[str] = Query(None),
    amount_to_pay: Optional[float] = Query(None),
    amount_to_pay_bis: Optional[float] = Query(None),
    amount_to_pay_operation: Optional[str] = Query(None),
    status: Optional[StatusArticle] = Query(None),
    start_date: Optional[date] = Query(None),
    start_date_bis: Optional[date] = Query(None),
    start_date_operation: Optional[str] = Query(None),
    end_date: Optional[date] = Query(None),
    end_date_bis: Optional[date] = Query(None),
    end_date_operation: Optional[str] = Query(None),
    refnumber: Optional[str] = Query(None),
    owner_id: Optional[str] = Query(None),
    subscription_id: Optional[str] = Query(None),
    town_id: Optional[str] = Query(None),
    category_article_id: Optional[str] = Query(None),
    article_state_id: Optional[str] = Query(None),
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
    # Appel à la fonction de recherche
    items, total_records = research(
        db=db,
        name=name,
        description=description,
        reception_place=reception_place,
        phone=phone,
        phone_transaction=phone_transaction,
        price=price,
        price_bis=price_bis,
        price_operation=price_operation,
        start_date=start_date,
        start_date_bis=start_date_bis,
        start_date_operation=start_date_operation,
        end_date=end_date,
        end_date_bis=end_date_bis,
        end_date_operation=end_date_operation,
        nb_visite=nb_visite,
        nb_visite_bis=nb_visite_bis,
        nb_visite_operation=nb_visite_operation,
        amount_to_pay=amount_to_pay,
        amount_to_pay_bis=amount_to_pay_bis,
        amount_to_pay_operation=amount_to_pay_operation,
        status=status,
        owner_id=owner_id,
        subscription_id=subscription_id,
        town_id=town_id,
        category_article_id=category_article_id,
        article_state_id=article_state_id,
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
        ArticleSchema(
            **item.__dict__,  # Sérialise l'objet principal
            owner=item.owner if item.owner else None,  # Inclure explicitement la relation town
            subscription=item.subscription if item.subscription else None,  # Inclure explicitement la relation town
            town=item.town if item.town else None,  # Inclure explicitement la relation town
            creator=get_user_by_id(db, item.created_by) if item.created_by else None,
            updator=get_user_by_id(db, item.updated_by) if item.updated_by else None
        )
        for item in items
    ]

    # Construction de la réponse paginée
    return PaginatedResponse[ArticleSchema](  # Utilisez PaginatedResponse[ArticleSchema]
        records=serialized,
        metadata=PaginationMetadata(
            total_records=total_records,
            total_pages=total_pages,
            current_page=current_page,
        ),
    )

@router.get("/{id}", response_model=ArticleSchema)
async def get_detail(id: str, db: Session = Depends(get_db)):
    item = get_by_id(db, id)
    if not item:
        raise HTTPException(status_code=404, detail="Article not found.")
    # Récupération du créateur
    # creator = get_user_by_id(db, item.created_by) if item.created_by else None
    # updator = get_user_by_id(db, item.updated_by) if item.updated_by else None
    owner=item.owner if item.owner else None,  # Inclure explicitement la relation town
    subscription=item.subscription if item.subscription else None,  # Inclure explicitement la relation town
    town=item.town if item.town else None,  # Inclure explicitement la relation town
    creator=get_user_by_id(db, item.created_by) if item.created_by else None,
    updator=get_user_by_id(db, item.updated_by) if item.updated_by else None

    # Retourne l'utilisateur avec le créateur sérialisé
    return ArticleSchema.from_orm(item).copy(update={
        "creator": creator,
        "updator": updator}
    )
    # return ArticleSchema.from_orm(item)


@router.put("/{id}", response_model=ArticleSchema)
async def update_route(
    id: str, 
    n_update: ArticleUpdate, 
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_user_from_token)
):
    try:
        item = update(db, id, n_update, current_user.id)
        # Récupération du créateur
        # creator = get_user_by_id(db, item.created_by) if item.created_by else None
        # updator = get_user_by_id(db, item.updated_by) if item.updated_by else None
        owner=item.owner if item.owner else None,  # Inclure explicitement la relation town
        subscription=item.subscription if item.subscription else None,  # Inclure explicitement la relation town
        town=item.town if item.town else None,  # Inclure explicitement la relation town
        creator=get_user_by_id(db, item.created_by) if item.created_by else None,
        updator=get_user_by_id(db, item.updated_by) if item.updated_by else None

        # Retourne l'utilisateur avec le créateur sérialisé
        return ArticleSchema.from_orm(item).copy(update={
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
        return {"message": "Article deleted!"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/restore/{id}", response_model=ArticleSchema)
async def restore_route(
    id: str, 
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_user_from_token)
):
    try:
        item = restore(db, id, current_user.id)
        # Récupération du créateur
        # creator = get_user_by_id(db, item.created_by) if item.created_by else None
        # updator = get_user_by_id(db, item.updated_by) if item.updated_by else None
        owner=item.owner if item.owner else None,  # Inclure explicitement la relation town
        subscription=item.subscription if item.subscription else None,  # Inclure explicitement la relation town
        town=item.town if item.town else None,  # Inclure explicitement la relation town
        creator=get_user_by_id(db, item.created_by) if item.created_by else None,
        updator=get_user_by_id(db, item.updated_by) if item.updated_by else None

        # Retourne l'utilisateur avec le créateur sérialisé
        return ArticleSchema.from_orm(item).copy(update={
            "creator": creator,
            "updator": updator}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))