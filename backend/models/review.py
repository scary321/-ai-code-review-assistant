from datetime import datetime
from extensions import db


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    review_score = db.Column(db.Float, nullable=False, default=0.0)
    summary = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    findings = db.relationship(
        "ReviewFinding", backref="review", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self, include_findings=True):
        data = {
            "id": self.id,
            "project_id": self.project_id,
            "review_score": self.review_score,
            "summary": self.summary,
            "created_at": self.created_at.isoformat(),
        }
        if include_findings:
            data["findings"] = [f.to_dict() for f in self.findings]
        return data

    def __repr__(self):
        return f"<Review {self.id} score={self.review_score}>"


class ReviewFinding(db.Model):
    __tablename__ = "review_findings"

    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey("reviews.id"), nullable=False)
    # critical | high | medium | low | info
    severity = db.Column(db.String(20), nullable=False, default="info")
    issue = db.Column(db.String(255), nullable=False)
    explanation = db.Column(db.Text, nullable=True)
    suggestion = db.Column(db.Text, nullable=True)
    file_name = db.Column(db.String(500), nullable=True)
    line_number = db.Column(db.Integer, nullable=True)
    # which engine raised it: pylint | bandit | radon | openai
    source = db.Column(db.String(20), nullable=False, default="pylint")

    def to_dict(self):
        return {
            "id": self.id,
            "review_id": self.review_id,
            "severity": self.severity,
            "issue": self.issue,
            "explanation": self.explanation,
            "suggestion": self.suggestion,
            "file_name": self.file_name,
            "line_number": self.line_number,
            "source": self.source,
        }

    def __repr__(self):
        return f"<Finding {self.issue} ({self.severity})>"
