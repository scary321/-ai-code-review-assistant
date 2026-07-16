from datetime import datetime
from extensions import db


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    project_name = db.Column(db.String(255), nullable=False)
    # 'single_file' or 'zip'
    upload_type = db.Column(db.String(20), nullable=False, default="single_file")
    # relative path under UPLOAD_FOLDER where the project's files live
    storage_path = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    reviews = db.relationship(
        "Review", backref="project", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "project_name": self.project_name,
            "upload_type": self.upload_type,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self):
        return f"<Project {self.project_name}>"
