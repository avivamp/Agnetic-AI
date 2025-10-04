# backend/app/models/search_interaction.py
from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from sqlalchemy import String, Float, Boolean, Integer, TIMESTAMP, text

Base = declarative_base()

class SearchInteraction(Base):
    __tablename__ = "search_interactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    query: Mapped[str] = mapped_column(String)
    product_id: Mapped[str] = mapped_column(String)
    merchant_id: Mapped[str] = mapped_column(String, nullable=True)

    # model / retrieval features we’ll reuse for training
    vector_similarity: Mapped[float] = mapped_column(Float, nullable=True)
    score: Mapped[float] = mapped_column(Float, nullable=True)   # raw pinecone score

    # personalization context
    cabin: Mapped[str] = mapped_column(String, nullable=True)
    loyalty_tier: Mapped[str] = mapped_column(String, nullable=True)
    user_id_hash: Mapped[str] = mapped_column(String, nullable=True)

    trip_from: Mapped[str] = mapped_column(String, nullable=True)
    trip_to: Mapped[str] = mapped_column(String, nullable=True)
    hours_to_departure: Mapped[int] = mapped_column(Integer, nullable=True)

    # labels
    clicked: Mapped[bool] = mapped_column(Boolean, default=False)
    purchased: Mapped[bool] = mapped_column(Boolean, default=False)

    timestamp: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("NOW()")
    )
