from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.users_schemas import (LoginResponse,
UserOutSchema,
TokenSchema,
UserSchema)
from app.crud.auth_crud import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    revoke_token,
    get_user_from_token,
    extract_user_from_token,
    get_privileges,
)
from app.models.models import User

# Configuration OAuth2
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/login",  # Assurez-vous que c'est bien "/login"
    description="Authentification via username et password pour obtenir un token JWT.",
)

router = APIRouter(tags=["Authentication"])

@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Route pour l'authentification de l'utilisateur.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
        )

    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    privileges = get_privileges(user.id, db)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user,
        "privileges": privileges,
    }

@router.post("/refresh-token", response_model=TokenSchema)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    user_data = extract_user_from_token(refresh_token, db, is_refresh=True)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de rafraîchissement invalide"
        )

    new_access_token = create_access_token(data={"sub": user_data["user_id"]})
    return {
        "access_token": new_access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Route pour déconnecter l'utilisateur.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token introuvable")

    revoke_token(token, db)
    return {"message": "Déconnexion réussie"}

@router.get("/me", response_model=UserSchema)
async def get_current_user(
    current_user: User = Depends(get_user_from_token),
    db: Session = Depends(get_db),
):
    """
    Récupère les informations de l'utilisateur actuellement connecté.
    """
    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé")
    return UserSchema.from_orm(current_user)