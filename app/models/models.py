from sqlalchemy import Enum,Column, Integer, String, Double, TIMESTAMP, Date, Boolean, DateTime, text,ForeignKey,ARRAY
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum

######################## User #############################
class GenderType(enum.Enum):
    M = 1
    F = 2
    
# User : doing
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, unique=True, nullable=False)
    refnumber = Column(String, unique=True, nullable=False)
    username = Column(String, index=True, unique=True, nullable=True)
    phone = Column(String, index=True , unique=True, nullable=True)
    email = Column(String, index=True, unique=True, nullable=False)
    birthday = Column(String, nullable=False)
    gender = Column(Enum(GenderType), nullable=True)
    image = Column(String, index=True, unique=True, nullable=True)
    password = Column(String(length=256), index=True)
    is_staff = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    town_id = Column(String, ForeignKey(
        "towns.id", ondelete="CASCADE"), nullable=False)
    town = relationship("Town", back_populates="owners")
    
    # Colonnes étrangères inversées
    signals = relationship("Signal", back_populates="owner")
    articles = relationship("Article", back_populates="owner")
 
# Country : doing    
class Country(Base):
    __tablename__ = "contries"

    id = Column(String, primary_key=True, index=True, unique=True, nullable=False)
    refnumber = Column(String, unique=True, nullable=False)
    name = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    
    # Colonnes étrangères inversées
    towns = relationship("Town", back_populates="country")

    

# Town : doing  
class Town(Base):
    __tablename__ = "towns"

    id = Column(String, primary_key=True, index=True, unique=True, nullable=False)
    refnumber = Column(String, unique=True, nullable=False)
    name = Column(String, unique=False, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    
    country_id = Column(String, ForeignKey(
        "contries.id", ondelete="CASCADE"), nullable=False)
    country = relationship("Country", back_populates="towns")
    
    # Colonnes étrangères inversées
    owners = relationship("User", back_populates="town")
    articles = relationship("Article", back_populates="town")



# Category : doing   
class CategoryArticle(Base):
    __tablename__ = "categorie_articles"

    id = Column(String, primary_key=True, index=True, unique=True, nullable=False)
    refnumber = Column(String, unique=True, nullable=False)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String(length=65535), nullable=False)
    image = Column(String, index=True, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    
    # Colonnes étrangères inversées
    articles = relationship("Article", back_populates="category")

# Article Status  : doing   
class ArticleStatus(Base):
    __tablename__ = "article_status"

    id = Column(String, primary_key=True, index=True, unique=True, nullable=False)
    refnumber = Column(String, unique=True, nullable=False)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String(length=65535), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    
    # Colonnes étrangères inversées
    articles = relationship("Article", back_populates="article_statu")
    
# Product : doing     
class Article(Base):
    __tablename__ = "articles"

    id = Column(String, primary_key=True, index=True, unique=True, nullable=False)
    refnumber = Column(String, unique=True, nullable=False)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String(length=65535), nullable=False)
    reception_place = Column(String(length=256), nullable=False)
    price = Column(Double, nullable=True)
    main_image = Column(String, index=True, unique=True, nullable=False)
    other_images = Column(ARRAY(String), index=True, nullable=True) 
    end_date = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    publish = Column(Boolean, default=False)
    locked = Column(Boolean, default=False)
    # relationship
    owner_id = Column(String, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User", back_populates="articles")
    town_id = Column(String, ForeignKey(
        "towns.id", ondelete="CASCADE"), nullable=False)
    town = relationship("Town", back_populates="articles")
    category_article_id = Column(String, ForeignKey(
        "categorie_articles.id", ondelete="CASCADE"), nullable=False)
    category = relationship("CategoryArticle", back_populates="articles")
    article_statu_id = Column(String, ForeignKey(
        "article_status.id", ondelete="CASCADE"), nullable=False)
    article_statu = relationship("ArticleStatus", back_populates="articles")# il s'agit des éléments en cour appartenant à la tables article_status
    # Colonnes étrangères inversées
    signals = relationship("Signal", back_populates="article")
    
   
# Signal : doing
class Signal(Base):
    __tablename__ = "signals"

    id = Column(String, primary_key=True, index=True, unique=True, nullable=False)
    refnumber = Column(String, unique=True, nullable=False)
    owner_id = Column(String, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User", back_populates="signals")
    
    article_id = Column(String, ForeignKey(
        "articles.id", ondelete="CASCADE"), nullable=False)
    article = relationship("Article", back_populates="signals")
    description = Column(String(length=65535), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    

