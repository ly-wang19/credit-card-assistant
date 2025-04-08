"""
知识库数据模型定义
包含信用卡信息、用户对话等核心数据模型
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class CreditCard(Base):
    """信用卡信息模型"""
    __tablename__ = "credit_cards"
    
    id = Column(Integer, primary_key=True, index=True)
    bank_name = Column(String(50), nullable=False)
    card_name = Column(String(100), nullable=False)
    card_type = Column(String(50))  # 普卡、金卡、白金卡等
    annual_fee = Column(String(50))
    benefits = Column(JSON)  # 权益信息
    requirements = Column(JSON)  # 申请条件
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CardDocument(Base):
    """信用卡文档向量存储"""
    __tablename__ = "card_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer, ForeignKey("credit_cards.id"))
    content = Column(Text, nullable=False)
    embedding = Column(JSON)  # 存储向量数据
    metadata = Column(JSON)  # 额外元数据
    created_at = Column(DateTime, default=datetime.utcnow)

class UserConversation(Base):
    """用户对话记录"""
    __tablename__ = "user_conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=False)
    session_id = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联的信用卡ID（如果有）
    card_id = Column(Integer, ForeignKey("credit_cards.id"), nullable=True)
    card = relationship("CreditCard") 