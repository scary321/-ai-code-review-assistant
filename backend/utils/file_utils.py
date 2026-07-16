import os
import uuid
import zipfile
from werkzeug.utils import secure_filename


def allowed_file(filename, allowed_extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def make_project_storage_dir(upload_root, user_id):
    """Create a unique folder for a project's uploaded files."""
    folder_name = f"user_{user_id}_{uuid.uuid4().hex[:10]}"
    full_path = os.path.join(upload_root, folder_name)
    os.makedirs(full_path, exist_ok=True)
    return folder_name, full_path


def safe_extract_zip(zip_path, extract_to):
    """
    Extract a zip file while guarding against Zip Slip path traversal attacks.
    Only .py files (and directories) are extracted; anything else is skipped.
    """
    extracted_py_files = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            member_path = os.path.normpath(member.filename)
            if member_path.startswith("..") or os.path.isabs(member_path):
                continue  # skip suspicious paths
            if member.is_dir():
                continue
            if not member.filename.lower().endswith(".py"):
                continue

            target_path = os.path.join(extract_to, member_path)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with zf.open(member) as source, open(target_path, "wb") as target:
                target.write(source.read())
            extracted_py_files.append(target_path)

    return extracted_py_files


def collect_python_files(root_dir):
    """Walk a directory and return all .py file paths."""
    py_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.endswith(".py"):
                py_files.append(os.path.join(dirpath, fname))
    return py_files


def secure_save(file_storage, destination_dir):
    """Save a Werkzeug FileStorage object with a sanitized filename."""
    filename = secure_filename(file_storage.filename)
    dest_path = os.path.join(destination_dir, filename)
    file_storage.save(dest_path)
    return filename, dest_path
