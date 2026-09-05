"""
Service for generating CSV and PDF reports.
"""
import csv
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from app.services.analytics_filters import AnalyticsFilters

class ReportingService:
    """Service class for generating CSV and PDF reports."""

    @staticmethod
    def generate_csv(user, filters):
        """Generates a CSV of issues the user is authorized to see."""
        query = AnalyticsFilters.get_base_issue_query(user, filters)
        issues = query.all()

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(['ID', 'Title', 'Status', 'Priority', 'Category ID', 'Created At'])

        for i in issues:
            priority_str = i.official_priority.name if i.official_priority else 'Unassigned'
            writer.writerow([
                i.id,
                i.title,
                i.status.name,
                priority_str,
                i.category_id,
                i.created_at.isoformat()
            ])

        return output.getvalue()

    @staticmethod
    def generate_pdf(user, filters):
        """Generates a simple PDF report."""
        query = AnalyticsFilters.get_base_issue_query(user, filters)
        issues = query.limit(100).all() # Limit for simple PDF layout

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, "CivicFix Issue Report")

        c.setFont("Helvetica", 10)
        y = 710
        for i in issues:
            priority_str = i.official_priority.name if i.official_priority else 'Unassigned'
            line = f"[{i.id}] {i.title} - Status: {i.status.name} - Priority: {priority_str}"
            c.drawString(50, y, line)
            y -= 20
            if y < 50:
                c.showPage()
                y = 750

        c.save()
        buffer.seek(0)
        return buffer.getvalue()
