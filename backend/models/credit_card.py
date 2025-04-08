from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class CreditCard(Base):
    __tablename__ = 'credit_cards'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    bank = Column(String(50), nullable=False)
    card_type = Column(String(50))
    credit_level = Column(String(50))
    card_organization = Column(String(50))
    annual_fee = Column(Text)  # JSON string
    points_rule = Column(Text)  # JSON string
    benefits = Column(Text)  # JSON string
    application_condition = Column(Text)  # JSON string
    foreign_transaction_fee = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<CreditCard {self.name} by {self.bank}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "bank": self.bank,
            "card_type": self.card_type,
            "credit_level": self.credit_level,
            "card_organization": self.card_organization,
            "annual_fee": self.annual_fee,
            "points_rule": self.points_rule,
            "benefits": self.benefits,
            "application_condition": self.application_condition,
            "foreign_transaction_fee": self.foreign_transaction_fee
        } 