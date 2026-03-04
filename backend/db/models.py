from datetime import UTC, datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, relationship


def _utcnow():
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, default="")
    template_path = Column(String, nullable=True)
    mapping_config = Column(JSON, default=dict)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    generation_runs = relationship(
        "GenerationRun", back_populates="project", cascade="all, delete-orphan"
    )


class GenerationRun(Base):
    __tablename__ = "generation_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    mapping_snapshot = Column(JSON, nullable=False)
    output_path = Column(String, nullable=True)
    report = Column(JSON, nullable=True)
    status = Column(String, default="completed")
    created_at = Column(DateTime, default=_utcnow)

    project = relationship("Project", back_populates="generation_runs")
