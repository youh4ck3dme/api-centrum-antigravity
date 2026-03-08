# backend/app/dns_monitor/threat_model.py

from sqlalchemy import Column, Integer, String, Text, BigInteger
from ..db import Base


class Threat(Base):
    __tablename__ = "threats"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(255), index=True, nullable=False)
    record_type = Column(String(10), nullable=True)
    severity = Column(String(20), nullable=False)
    message = Column(Text, nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    timestamp = Column(BigInteger, index=True, nullable=False)
