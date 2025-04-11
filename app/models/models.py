from sqlalchemy import Enum, Column, Float, Integer, String, DateTime, Date, Boolean, Text, ForeignKey, ARRAY, text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, validates
from app.database import Base
import enum

# =============================== ENUMERATIONS ===============================
class GenderType(enum.Enum):
    M = 1
    F = 2

class StatusProposition(enum.Enum):
    ACTIF = "actif"
    INACTIF = "inactif"

class StatusArticle(enum.Enum):
    EN_ATTENTE = "en attente"
    PUBLIEE = "publié"
    EXPIRE = "expiré"
    ABANDONNE = "abandonné"

# =============================== BASE MIXIN ===============================
class BaseMixin:
    id = Column(String, primary_key=True, index=True, unique=True, nullable=False)
    refnumber = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    active = Column(Boolean, default=True)

# =============================== USER ===============================
class User(BaseMixin, Base):
    __tablename__ = "users"
    username = Column(String(255), index=True, unique=True, nullable=False)
    phone = Column(String(15), index=True, unique=True, nullable=True)
    email = Column(String(255), index=True, unique=True, nullable=False)
    birthday = Column(Date, nullable=True)
    gender = Column(Enum(GenderType), nullable=True)
    image = Column(String(255), nullable=True)
    password = Column(String(256), nullable=False)
    is_staff = Column(Boolean, default=False)
    town_id = Column(String, ForeignKey("towns.id", ondelete="CASCADE"), nullable=False)
    town = relationship("Town", back_populates="owners")

    # Relationships
    owned_articles = relationship("Article", back_populates="owner")
    
    # Signalements faits par cet utilisateur
    reported_signals = relationship(
        "Signal",
        foreign_keys="Signal.owner_id",  # Clé étrangère explicite
        back_populates="owner"
    )
    
    # Signalements où cet utilisateur est l'offenseur
    offender_signals = relationship(
        "Signal",
        foreign_keys="Signal.offender_id",  # Clé étrangère explicite
        back_populates="offender"
    )
    
    favorites = relationship("Favorite", back_populates="owner")
    subscriptions = relationship("Subscription", back_populates="owner")
    privilege_users = relationship("PrivilegeUser", back_populates="owner")
    user_roles = relationship("UserRole", back_populates="owner")

# =============================== PRIVILEGE ===============================
class Privilege(BaseMixin, Base):
    __tablename__ = "privileges"
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)

    # Relationships
    privilege_users = relationship("PrivilegeUser", back_populates="privilege")
    privilege_roles = relationship("PrivilegeRole", back_populates="privilege")

# =============================== ROLE ===============================
class Role(BaseMixin, Base):
    __tablename__ = "roles"
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)

    # Relationships
    privilege_roles = relationship("PrivilegeRole", back_populates="role")
    user_roles = relationship("UserRole", back_populates="role")

# =============================== PrivilegeRole ===============================
class PrivilegeRole(BaseMixin, Base):
    __tablename__ = "privilege_roles"
    role_id = Column(String, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    role = relationship("Role", back_populates="privilege_roles")
    privilege_id = Column(String, ForeignKey("privileges.id", ondelete="CASCADE"), nullable=False)
    privilege = relationship("Privilege", back_populates="privilege_roles")

# =============================== PrivilegeUser ===============================
class PrivilegeUser(BaseMixin, Base):
    __tablename__ = "privilege_users"
    owner_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User", back_populates="privilege_users")
    privilege_id = Column(String, ForeignKey("privileges.id", ondelete="CASCADE"), nullable=False)
    privilege = relationship("Privilege", back_populates="privilege_users")

# =============================== UserRole ===============================
class UserRole(BaseMixin, Base):
    __tablename__ = "user_roles"
    owner_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User", back_populates="user_roles")
    role_id = Column(String, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    role = relationship("Role", back_populates="user_roles")

# =============================== COUNTRY ===============================
class Country(BaseMixin, Base):
    __tablename__ = "countries"
    name = Column(String(255), unique=True, index=True, nullable=False)

    # Relationships
    towns = relationship("Town", back_populates="country")

# =============================== TOWN ===============================
class Town(BaseMixin, Base):
    __tablename__ = "towns"
    name = Column(String(255), index=True, nullable=False)
    country_id = Column(String, ForeignKey("countries.id", ondelete="CASCADE"), nullable=False)
    country = relationship("Country", back_populates="towns")

    # Relationships
    owners = relationship("User", back_populates="town")
    articles = relationship("Article", back_populates="town")

# =============================== Catégorie d'article ===============================
class CategoryArticle(BaseMixin, Base):
    __tablename__ = "category_articles"
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    image = Column(String(255), nullable=True)

    # Relationships
    articles = relationship("Article", back_populates="category")

# =============================== ArticleState ===============================
class ArticleState(BaseMixin, Base):
    __tablename__ = "article_states"
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)

    # Relationships
    articles = relationship("Article", back_populates="article_state")

# =============================== Article ===============================
class Article(BaseMixin, Base):
    __tablename__ = "articles"
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    reception_place = Column(String(255), nullable=False)
    phone = Column(String(15), index=True, nullable=True)
    phone_transaction = Column(String(15), index=True, nullable=True)
    price = Column(Float, nullable=True)
    main_image = Column(String(255), nullable=False)
    other_images = Column(ARRAY(String), nullable=True)
    end_date = Column(Date, nullable=True)
    nb_visite = Column(Integer, server_default=text("0"))
    status = Column(Enum(StatusArticle), nullable=True)
    daily_rate = Column(Float, nullable=True)
    owner_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    owner = relationship("User", back_populates="owned_articles")
    subscription_id = Column(String, ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=True)
    subscription = relationship("Subscription", back_populates="articles")
    town_id = Column(String, ForeignKey("towns.id", ondelete="CASCADE"), nullable=False)
    town = relationship("Town", back_populates="articles")
    category_article_id = Column(String, ForeignKey("category_articles.id", ondelete="CASCADE"), nullable=False)
    category = relationship("CategoryArticle", back_populates="articles")
    article_state_id = Column(String, ForeignKey("article_states.id", ondelete="CASCADE"), nullable=False)  # Correction ici
    article_state = relationship("ArticleState", back_populates="articles")  # Correction ici
    signals = relationship("Signal", back_populates="article")
    favorites = relationship("Favorite", back_populates="article")
    notifications = relationship("Notification", back_populates="article")
    payments = relationship("Payment", back_populates="article")

# =============================== Signal ===============================
class Signal(BaseMixin, Base):
    __tablename__ = "signals"
    
    owner_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship(
        "User",
        foreign_keys=[owner_id],  # Clé étrangère explicite
        back_populates="reported_signals"
    )
    
    offender_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    offender = relationship(
        "User",
        foreign_keys=[offender_id],  # Clé étrangère explicite
        back_populates="offender_signals"
    )
    
    article_id = Column(String, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    article = relationship("Article", back_populates="signals")
    
    description = Column(Text, nullable=False)

# =============================== Favorite ===============================
class Favorite(BaseMixin, Base):
    __tablename__ = "favorites"
    owner_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User", back_populates="favorites")
    article_id = Column(String, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    article = relationship("Article", back_populates="favorites")

# =============================== Notification ===============================
class Notification(BaseMixin, Base):
    __tablename__ = "notifications"
    article_id = Column(String, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    article = relationship("Article", back_populates="notifications")
    description = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False)

# =============================== SubscriptionType ===============================
class SubscriptionType(BaseMixin, Base):
    __tablename__ = "subscription_types"
    name = Column(String(255), unique=True, index=True, nullable=False)
    advertisements = Column(Integer, nullable=False)
    price = Column(Float, nullable=True)
    price_max_article = Column(Float, nullable=True)
    duration = Column(Integer, nullable=True)
    status = Column(Enum(StatusProposition), nullable=False, default="actif")

    # Relationships
    subscriptions = relationship("Subscription", back_populates="subscription_type")

# =============================== Subscription ===============================
class Subscription(BaseMixin, Base):
    __tablename__ = "subscriptions"
    subscription_type_id = Column(String, ForeignKey("subscription_types.id", ondelete="CASCADE"), nullable=False)
    subscription_type = relationship("SubscriptionType", back_populates="subscriptions")
    owner_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User", back_populates="subscriptions")
    description = Column(Text, nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=False)
    expiration_date = Column(DateTime(timezone=True), nullable=False)
    remaining_advertisements = Column(Integer, nullable=False)
    is_read = Column(Boolean, default=False)

    # Relationships
    articles = relationship("Article", back_populates="subscription")
    payments = relationship("Payment", back_populates="subscription")

# =============================== TaxInterval ===============================
class TaxInterval(BaseMixin, Base):
    __tablename__ = "tax_intervals"
    min_price = Column(Float, nullable=True)
    max_price = Column(Float, nullable=True)
    daily_rate = Column(Float, nullable=True)
    is_read = Column(Boolean, default=False)

    @validates('min_price', 'max_price')
    def validate_price_range(self, key, value):
        if key == 'max_price' and self.min_price is not None and value is not None:
            if self.min_price > value:
                raise ValueError("max_price doit être supérieur ou égal à min_price.")
        return value

# =============================== Payment ===============================
class Payment(BaseMixin, Base):
    __tablename__ = "payments"
    payment_number = Column(String, unique=True, nullable=True)
    article_id = Column(String, ForeignKey("articles.id", ondelete="CASCADE"), nullable=True)
    article = relationship("Article", back_populates="payments")
    subscription_id = Column(String, ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=True)
    subscription = relationship("Subscription", back_populates="payments")
    is_read = Column(Boolean, default=False)

# =============================== SlidingScaleTariffs ===============================
class SlidingScaleTariffs(BaseMixin, Base):  # Correction du nom de la classe
    __tablename__ = "sliding_scale_tariffs"  # Suppression de l'espace au début
    days_min = Column(Integer, nullable=False)
    max_days = Column(Integer, nullable=False)
    rate = Column(Float, nullable=False)

    @validates('days_min', 'max_days')  # Correction du nom des colonnes validées
    def validate_days_range(self, key, value):
        if key == 'max_days' and self.days_min is not None and value is not None:
            if self.days_min > value:
                raise ValueError("max_days doit être supérieur ou égal à days_min.")
        return value

# =============================== VolumeDiscounts ===============================
class VolumeDiscounts(BaseMixin, Base):
    __tablename__ = "volume_discounts"  # Suppression de l'espace au début
    threshold = Column(Integer, nullable=False)
    reduction = Column(Float, nullable=False)

class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(String, primary_key=True, index=True)  # ID unique du token
    token = Column(String, unique=True, index=True)    # Le token révoqué
    revoked_at = Column(DateTime(timezone=True), server_default=func.now())  # Date de révocation
    is_revoked = Column(Boolean, default=True)         # Statut de révocation