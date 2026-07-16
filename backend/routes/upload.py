import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models.project import Project
from utils.file_utils import (
    allowed_file,
    make_project_storage_dir,
    safe_extract_zip,
    secure_save,
)

upload_bp = Blueprint("upload", __name__, url_prefix="/api/upload")


@upload_bp.post("")
@jwt_required()
def upload_project():
    user_id = get_jwt_identity()

    if "file" not in request.files:
        return jsonify({"error": "no file part in request"}), 400

    file = request.files["file"]
    project_name = request.form.get("project_name", "").strip() or file.filename

    if file.filename == "":
        return jsonify({"error": "no file selected"}), 400

    allowed_ext = current_app.config["ALLOWED_EXTENSIONS"]
    if not allowed_file(file.filename, allowed_ext):
        return jsonify({"error": f"file type not allowed, must be one of {sorted(allowed_ext)}"}), 400

    upload_root = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_root, exist_ok=True)
    folder_name, full_path = make_project_storage_dir(upload_root, user_id)

    is_zip = file.filename.lower().endswith(".zip")

    if is_zip:
        zip_temp_path = os.path.join(full_path, "upload.zip")
        file.save(zip_temp_path)
        extracted = safe_extract_zip(zip_temp_path, full_path)
        os.remove(zip_temp_path)
        if not extracted:
            return jsonify({"error": "zip contained no .py files"}), 400
        upload_type = "zip"
    else:
        secure_save(file, full_path)
        upload_type = "single_file"

    project = Project(
        user_id=user_id,
        project_name=project_name,
        upload_type=upload_type,
        storage_path=folder_name,
    )
    db.session.add(project)
    db.session.commit()

    return jsonify({"project": project.to_dict()}), 201


@upload_bp.get("")
@jwt_required()
def list_projects():
    user_id = get_jwt_identity()
    projects = (
        Project.query.filter_by(user_id=user_id)
        .order_by(Project.created_at.desc())
        .all()
    )
    return jsonify({"projects": [p.to_dict() for p in projects]}), 200
