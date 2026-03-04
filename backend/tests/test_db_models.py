"""Tests for database models: Project and GenerationRun."""

import tempfile
from pathlib import Path

import pytest

from db.database import init_db
from db.models import GenerationRun, Project


@pytest.fixture
def db_session():
    """Create a temporary SQLite database and yield a session."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "test.db"
        session_factory = init_db(str(db_path))
        session = session_factory()
        try:
            yield session
        finally:
            session.close()


class TestCreateGenerationRun:
    def test_create_generation_run(self, db_session):
        """Create Project + GenerationRun, verify relationship."""
        project = Project(name="Test Project", description="A test project")
        db_session.add(project)
        db_session.flush()

        run = GenerationRun(
            project_id=project.id,
            mapping_snapshot={"m1": {"data_source": "data.csv", "field": "Author"}},
            output_path="/output/test.docx",
            status="completed",
        )
        db_session.add(run)
        db_session.commit()

        # Verify relationship
        fetched_project = db_session.query(Project).filter_by(id=project.id).first()
        assert fetched_project is not None
        assert len(fetched_project.generation_runs) == 1
        assert fetched_project.generation_runs[0].id == run.id
        assert fetched_project.generation_runs[0].project_id == project.id
        assert fetched_project.generation_runs[0].status == "completed"


class TestGenerationRunStoresReport:
    def test_generation_run_stores_report(self, db_session):
        """Store JSON report in GenerationRun, retrieve it."""
        project = Project(name="Report Project")
        db_session.add(project)
        db_session.flush()

        report_data = {
            "total_markers": 5,
            "rendered": 4,
            "skipped": 1,
            "warnings": [{"level": "warning", "message": "Unmapped marker"}],
            "errors": [],
            "results": [
                {"marker_id": "m1", "success": True},
                {"marker_id": "m2", "success": True},
                {"marker_id": "m3", "success": True},
                {"marker_id": "m4", "success": True},
                {"marker_id": "m5", "success": False, "error": "No data"},
            ],
        }

        run = GenerationRun(
            project_id=project.id,
            mapping_snapshot={"markers": ["m1", "m2", "m3", "m4", "m5"]},
            report=report_data,
            status="completed",
        )
        db_session.add(run)
        db_session.commit()

        # Re-fetch from DB
        fetched_run = db_session.query(GenerationRun).filter_by(id=run.id).first()
        assert fetched_run is not None
        assert fetched_run.report is not None
        assert fetched_run.report["total_markers"] == 5
        assert fetched_run.report["rendered"] == 4
        assert fetched_run.report["skipped"] == 1
        assert len(fetched_run.report["warnings"]) == 1
        assert len(fetched_run.report["results"]) == 5


class TestProjectCascadeDelete:
    def test_project_cascade_delete(self, db_session):
        """Delete project -> generation runs also deleted."""
        project = Project(name="Cascade Project")
        db_session.add(project)
        db_session.flush()

        run1 = GenerationRun(
            project_id=project.id,
            mapping_snapshot={"run": 1},
            status="completed",
        )
        run2 = GenerationRun(
            project_id=project.id,
            mapping_snapshot={"run": 2},
            status="completed",
        )
        db_session.add_all([run1, run2])
        db_session.commit()

        # Verify both runs exist
        runs = db_session.query(GenerationRun).filter_by(project_id=project.id).all()
        assert len(runs) == 2

        # Delete the project
        db_session.delete(project)
        db_session.commit()

        # Verify project is gone
        assert db_session.query(Project).filter_by(id=project.id).first() is None

        # Verify generation runs are cascaded-deleted
        remaining_runs = db_session.query(GenerationRun).all()
        assert len(remaining_runs) == 0
