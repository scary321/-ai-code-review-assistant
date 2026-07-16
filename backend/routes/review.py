import os
from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models.project import Project
from models.review import Review, ReviewFinding
from utils.file_utils import collect_python_files
from utils.scoring import calculate_review_score, severity_breakdown
from services.pylint_service import run_pylint
from services.bandit_service import run_bandit
from services.radon_service import run_radon
from services.openai_service import run_ai_review
from services.documentation_service import generate_summary

review_bp = Blueprint("review", __name__, url_prefix="/api/review")


@review_bp.post("/<int:project_id>/run")
@jwt_required()
def run_review(project_id):
    user_id = get_jwt_identity()
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return jsonify({"error": "project not found"}), 404

    upload_root = current_app.config["UPLOAD_FOLDER"]
    project_dir = os.path.join(upload_root, project.storage_path)
    py_files = collect_python_files(project_dir)

    if not py_files:
        return jsonify({"error": "no Python files found for this project"}), 400

    all_findings = []
    for file_path in py_files:
        relative_name = os.path.relpath(file_path, project_dir)
        all_findings.extend(run_pylint(file_path, relative_name))
        all_findings.extend(run_bandit(file_path, relative_name))
        all_findings.extend(run_radon(file_path, relative_name))
        all_findings.extend(run_ai_review(file_path, relative_name))

    score = calculate_review_score(all_findings)
    summary = generate_summary(all_findings, project.project_name)

    review = Review(project_id=project.id, review_score=score, summary=summary)
    db.session.add(review)
    db.session.flush()  # get review.id before inserting findings

    for f in all_findings:
        db.session.add(
            ReviewFinding(
                review_id=review.id,
                severity=f.get("severity", "info"),
                issue=f.get("issue", "issue"),
                explanation=f.get("explanation"),
                suggestion=f.get("suggestion"),
                file_name=f.get("file_name"),
                line_number=f.get("line_number"),
                source=f.get("source", "pylint"),
            )
        )
    db.session.commit()

    response = review.to_dict()
    response["severity_breakdown"] = severity_breakdown(all_findings)
    return jsonify({"review": response}), 201


@review_bp.get("/<int:project_id>")
@jwt_required()
def list_reviews(project_id):
    user_id = get_jwt_identity()
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return jsonify({"error": "project not found"}), 404

    reviews = (
        Review.query.filter_by(project_id=project_id)
        .order_by(Review.created_at.desc())
        .all()
    )
    return jsonify({"reviews": [r.to_dict(include_findings=False) for r in reviews]}), 200


@review_bp.get("/detail/<int:review_id>")
@jwt_required()
def review_detail(review_id):
    user_id = get_jwt_identity()
    review = Review.query.get(review_id)
    if not review or review.project.user_id != int(user_id):
        return jsonify({"error": "review not found"}), 404
    return jsonify({"review": review.to_dict(include_findings=True)}), 200
