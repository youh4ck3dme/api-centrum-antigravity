# backend/app/domains/models.py

# Voliteľné: SQLAlchemy modely ak chceš persistenciu lokálne

from sqlalchemy import Column, Integer, String, Text
from ..db import Base


class Domain(Base):
    __tablename__ = "domains"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)

