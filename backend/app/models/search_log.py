from sqlalchemy import Column, Integer, String, Text, Float, Boolean, TIMESTAMP, JSON, func
from app.db import Base

class SearchLog(Base):
    __tablename__ = "search_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(TIMESTAMP, server_default=func.now())
    merchant_id = Column(String(50), nullable=False)
    session_id = Column(String(100), nullable=False)
    user_id = Column(String(100), nullable=True)
    query = Column(Text, nullable=False)
    query_embedding = Column(JSON, nullable=True)
    latency_ms = Column(Integer)
    results_count = Column(Integer)
    top_result_id = Column(String(50))
    top_result_score = Column(Float)
    selected_product_id = Column(String(50), nullable=True)
    conversion = Column(Boolean, default=False)
    error_flag = Column(Boolean, default=False)
    client_type = Column(String(50))
    country = Column(String(50))
