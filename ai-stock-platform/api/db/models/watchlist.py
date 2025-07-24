# Use the same Base and mixins as the rest of the models so that SQLAlchemy
# registers this model on the shared metadata.  Using a different Base causes
# relationship resolution errors such as the "Watchlist" class not being found
# when the ``User`` model is imported before this module.
from db.base import Base, TimestampMixin
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship


class Watchlist(Base, TimestampMixin):
    __tablename__ = "watchlists"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_public = Column(Boolean, default=False)

    # Relationships
    user = relationship(
        "User",
        back_populates="watchlists",
        overlaps="watchlist_entries,user"
    )
    stocks = relationship(
        "WatchlistStock",
        back_populates="watchlist",
        cascade="all, delete-orphan",
    )
