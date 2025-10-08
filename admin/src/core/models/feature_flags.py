from core.database import Base, db
from sqlalchemy import ForeignKeyConstraint, Integer, Column, String, Boolean
from sqlalchemy.orm import Mapped, relationship
from typing import List

from core.models.feature_flags_history import FeatureFlagHistory

class FeatureFlag(Base):
    __tablename__ = "feature_flags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    activated = Column(Boolean, nullable=False, default=False)
    description = Column(String, nullable=True)
    ForeignKeyConstraint(['id'], ['feature_flags_history.id'])
    history: Mapped["FeatureFlagHistory"] = relationship(
        "FeatureFlagHistory",
        back_populates="feature_flag",
        cascade="all, delete-orphan",
        order_by="FeatureFlagHistory.time",
    )
    def __repr__(self):
        return f"<Feature Flag {self.id}: {self.activated} last modified at {self.history.time if self.history else 'N/A'}>"


def list_feature_flags(page=1, per_page=10):
    query = db.session.query(FeatureFlag)
    total = query.count()
    flags = query.offset((page - 1) * per_page).limit(per_page).all()
    return flags, total


def create_feature_flag(**kwargs):
    flag = FeatureFlag(**kwargs)
    db.session.add(flag)
    db.session.commit()
    return flag


def update_feature_flag(id, **kwargs):
    flag = get_feature_flag(id)
    for key, value in kwargs.items():
        setattr(flag, key, value)
    db.session.commit()
    return flag

def toggle_feature_flag(id):
    flag = get_feature_flag(id)
    flag.activated = not flag.activated
    db.session.commit()
    return flag


def get_feature_flag(id):
    return db.session.query(FeatureFlag).filter(FeatureFlag.id == id).first()


def delete_feature_flag(id):
    flag = get_feature_flag(id)
    db.session.delete(flag)
    db.session.commit()
    return flag
