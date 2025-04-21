from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.schemas.signals_schemas import (
    SignalCreate,
    SignalUpdate,
    SignalSchema,)
from app.schemas.utils_schemas import (PaginatedResponse,
PaginationMetadata,
ArticleSchema,
UserInfo,
)
from app.database import get_db
from typing import Optional, List
from datetime import date, datetime, time
from app.crud.signal_crud import (
    research,
    create,
    get_by_id,
)
from app.utils.utils import verify,get_user_by_id
from app.crud.auth_crud import (get_user_from_token_optional,
get_user_from_token)

router = APIRouter(prefix="/signals", tags=["Signals Requests"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SignalSchema)
async def create_route(
    item: SignalCreate, 
    db: Session = Depends(get_db), 
    current_user: Optional[str] = Depends(get_user_from_token)
):
    try:
        item = create(db, item, current_user.id if current_user else None)
        # Récupération du créateur
        creator = get_user_by_id(db, item.created_by) if item.created_by else None
        updator = get_user_by_id(db, item.updated_by) if item.updated_by else None

        # Retourne le PrivilegeUser avec le créateur sérialisé
        return SignalSchema.from_orm(item).copy(update={
            "creator": creator,
            "updator": updator}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# @router.get("/", response_model=PaginatedResponse[SignalSchema])  # Spécifiez SignalSchema ici
# async def research_route(
#     owner_id: Optional[str] = Query(None),
#     article_id: Optional[str] = Query(None),
#     offender_id: Optional[str] = Query(None),
#     description: Optional[str] = Query(None),
#     refnumber: Optional[str] = Query(None),
#     created_by: Optional[str] = Query(None),
#     created_at: Optional[date] = Query(None),
#     created_at_bis: Optional[date] = Query(None),
#     created_at_operation: Optional[str] = Query(None),
#     updated_by: Optional[str] = Query(None),
#     updated_at: Optional[date] = Query(None),
#     updated_at_bis: Optional[date] = Query(None),
#     updated_at_operation: Optional[str] = Query(None),
#     active: Optional[bool] = Query(None),
#     order: str = "asc",
#     sort_by: str = "created_at",
#     skip: int = 0,
#     limit: int = 100,
#     db: Session = Depends(get_db),
# ):
#     # Appel à la fonction de recherche
#     items, total_records = research(
#         db=db,
#         owner_id=owner_id,
#         article_id=article_id,
#         offender_id=offender_id,
#         description=description,
#         refnumber=refnumber,
#         created_by=created_by,
#         created_at=created_at,
#         created_at_bis=created_at_bis,
#         created_at_operation=created_at_operation,
#         updated_by=updated_by,
#         updated_at=updated_at,
#         updated_at_bis=updated_at_bis,
#         updated_at_operation=updated_at_operation,
#         active=active,
#         order=order,
#         sort_by=sort_by,
#         skip=skip,
#         limit=limit,
#     )

#     # Calcul du nombre total de pages
#     if limit == -1:
#         total_pages = 1  # Tous les utilisateurs actifs sont renvoyés
#         current_page = 1
#     else:
#         total_pages = (total_records // limit) + 1 if limit > 0 else 1
#         current_page = (skip // limit) + 1 if limit > 0 else 1


#     # Transformation des objets SQLAlchemy en instances Pydantic
#     serialized = [
#         SignalSchema(
#             id=item.id,
#             owner_id=item.owner_id,
#             article_id=item.article_id,
#             offender_id=item.offender_id,
#             description=item.description,
#             refnumber=item.refnumber,
#             created_at=item.created_at,
#             updated_at=item.updated_at,
#             active=item.active,
#             owner=UserInfo.model_validate(item.owner),  # Transforme la relation role en Ownerschema
#             offender=UserInfo.model_validate(item.offender)if item.offender else None,  # Transforme la relation role en Ownerschema
#             article=ArticleSchema.model_validate(item.article)if item.article else None,  # Transforme la relation article en ArticleSchema
#             creator=get_user_by_id(db, item.created_by) if item.created_by else None,
#             updator=get_user_by_id(db, item.updated_by) if item.updated_by else None
#         )
#         for item in items
#     ]

#     # Construction de la réponse paginée
#     return PaginatedResponse[SignalSchema](  # Utilisez PaginatedResponse[SignalSchema]
#         records=serialized,
#         metadata=PaginationMetadata(
#             total_records=total_records,
#             total_pages=total_pages,
#             current_page=current_page,
#         ),
#     )
@router.get("/", response_model=PaginatedResponse[SignalSchema])
async def get_signals(
    owner_id: Optional[str] = Query(None, description="Filtrer par ID du propriétaire"),
    article_id: Optional[str] = Query(None, description="Filtrer par ID de l'article"),
    offender_id: Optional[str] = Query(None, description="Filtrer par ID de l'offenseur"),
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
        owner_id=owner_id,
        article_id=article_id,
        offender_id=offender_id,
        description=description,
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
    # serialized = [SignalSchema.from_orm(item) for item in items]
    serialized = [
    SignalSchema(
        id=item.id,
        owner_id=item.owner_id,
        article_id=item.article_id,
        offender_id=item.offender_id,
        description=item.description,
        refnumber=item.refnumber,
        created_at=item.created_at,
        updated_at=item.updated_at,
        active=item.active,
        # owner=UserInfo.model_validate(item.owner),  # Transforme la relation role en Ownerschema
        # offender=UserInfo.model_validate(item.offender)if item.offender else None,  # Transforme la relation role en Ownerschema
        # article=ArticleSchema.model_validate(item.article)if item.article else None,  # Transforme la relation article en ArticleSchema
        creator=get_user_by_id(db, item.created_by) if item.created_by else None,
        updator=get_user_by_id(db, item.updated_by) if item.updated_by else None
    )
    for item in items
        ]

    # Construction de la réponse paginée
    return PaginatedResponse[SignalSchema](
        records=serialized,
        metadata=PaginationMetadata(
            total_records=total_records,
            total_pages=total_pages,
            current_page=current_page,
        ),
    )

@router.get("/{id}", response_model=SignalSchema)
async def get_detail(id: str, db: Session = Depends(get_db)):
    item = get_by_id(db, id)
    print("item : ", item)
    if not item:
        raise HTTPException(status_code=404, detail="Signal not found.")
    # Récupération du créateur
    creator = get_user_by_id(db, item.created_by) if item.created_by else None
    updator = get_user_by_id(db, item.updated_by) if item.updated_by else None

    # Retourne le PrivilegeUser avec le créateur sérialisé
    return SignalSchema.from_orm(item).copy(update={
        "creator": creator,
        "updator": updator}
    )