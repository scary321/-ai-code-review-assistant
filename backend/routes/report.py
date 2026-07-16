import os
from flask import Blueprint, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from models.review import Review

report_bp = Blueprint("report", __name__, url_prefix="/api/report")

_SEVERITY_COLORS = {
    "critical": colors.HexColor("#7f1d1d"),
    "high": colors.HexColor("#b91c1c"),
    "medium": colors.HexColor("#d97706"),
    "low": colors.HexColor("#2563eb"),
    "info": colors.HexColor("#6b7280"),
}


@report_bp.post("/<int:review_id>/generate")
@jwt_required()
def generate_report(review_id):
    user_id = get_jwt_identity()
    review = Review.query.get(review_id)
    if not review or review.project.user_id != int(user_id):
        return jsonify({"error": "review not found"}), 404

    reports_dir = current_app.config["REPORTS_FOLDER"]
    os.makedirs(reports_dir, exist_ok=True)
    filename = f"review_{review.id}_report.pdf"
    file_path = os.path.join(reports_dir, filename)

    _build_pdf(file_path, review)

    return jsonify({"report_file": filename, "download_url": f"/api/report/{review.id}/download"}), 201


@report_bp.get("/<int:review_id>/download")
@jwt_required()
def download_report(review_id):
    user_id = get_jwt_identity()
    review = Review.query.get(review_id)
    if not review or review.project.user_id != int(user_id):
        return jsonify({"error": "review not found"}), 404

    reports_dir = current_app.config["REPORTS_FOLDER"]
    filename = f"review_{review.id}_report.pdf"
    file_path = os.path.join(reports_dir, filename)

    if not os.path.exists(file_path):
        _build_pdf(file_path, review)

    return send_file(file_path, as_attachment=True, download_name=filename)


def _build_pdf(file_path, review):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleStyle", parent=styles["Title"], textColor=colors.HexColor("#111827")
    )
    heading_style = ParagraphStyle(
        "HeadingStyle", parent=styles["Heading2"], textColor=colors.HexColor("#1f2937")
    )
    body_style = styles["BodyText"]

    doc = SimpleDocTemplate(file_path, pagesize=letter, topMargin=0.6 * inch, bottomMargin=0.6 * inch)
    story = []

    project = review.project
    story.append(Paragraph("AI Code Review Report", title_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"Project: {project.project_name}", body_style))
    story.append(Paragraph(f"Review Date: {review.created_at.strftime('%Y-%m-%d %H:%M UTC')}", body_style))
    story.append(Paragraph(f"Overall Score: {review.review_score} / 100", body_style))
    story.append(Spacer(1, 14))

    story.append(Paragraph("Summary", heading_style))
    story.append(Paragraph((review.summary or "No summary available.").replace("\n", "<br/>"), body_style))
    story.append(Spacer(1, 14))

    story.append(Paragraph("Findings", heading_style))
    story.append(Spacer(1, 6))

    table_data = [["Severity", "Issue", "File / Line", "Suggestion"]]
    for f in sorted(review.findings, key=lambda x: _severity_rank(x.severity)):
        table_data.append(
            [
                Paragraph(f.severity.upper(), body_style),
                Paragraph(f.issue, body_style),
                Paragraph(f"{f.file_name or '-'}:{f.line_number or '-'}", body_style),
                Paragraph(f.suggestion or "-", body_style),
            ]
        )

    if len(table_data) == 1:
        table_data.append(["-", "No issues found", "-", "-"])

    table = Table(table_data, colWidths=[0.8 * inch, 1.8 * inch, 1.6 * inch, 2.4 * inch], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
            ]
        )
    )
    story.append(table)

    doc.build(story)


def _severity_rank(severity):
    order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    return order.get(severity, 5)
