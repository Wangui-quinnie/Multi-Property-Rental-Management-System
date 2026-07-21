from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from .receipt import get_receipt_data


def render_receipt_pdf(*, payment):
    """
    Renders the same data get_receipt_data() produces into a PDF
    document. Deliberately reuses that function rather than
    re-deriving receipt data separately — JSON and PDF receipts are
    always guaranteed to show identical figures, since they come
    from the exact same source.
    """
    data = get_receipt_data(payment=payment)

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("ReceiptTitle", parent=styles["Title"], fontSize=18, spaceAfter=6)
    heading_style = ParagraphStyle("ReceiptHeading", parent=styles["Heading2"], spaceAfter=4)
    normal_style = styles["Normal"]

    elements = []

    elements.append(Paragraph("Payment Receipt", title_style))
    elements.append(Paragraph(f"Receipt No: {data['receipt_number']}", normal_style))
    elements.append(Spacer(1, 0.5 * cm))

    details_table_data = [
        ["Payment Reference", data["payment_reference"]],
        ["Payment Method", data["payment_method"]],
        ["Payment Date", data["payment_date"].strftime("%Y-%m-%d %H:%M")],
        ["Tenant", data["tenant_name"]],
        ["Email", data["tenant_email"]],
        ["Amount Paid", f"{data['amount_paid']:,.2f}"],
    ]
    details_table = Table(details_table_data, colWidths=[5 * cm, 10 * cm])
    details_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.grey),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
    ]))
    elements.append(details_table)
    elements.append(Spacer(1, 0.8 * cm))

    elements.append(Paragraph("Allocation Breakdown", heading_style))

    if data["allocations"]:
        allocation_header = ["Invoice No", "Property", "Unit", "Amount Allocated"]
        allocation_rows = [
            [
                line["invoice_number"],
                line["property_name"],
                line["unit_number"],
                f"{line['amount_allocated']:,.2f}",
            ]
            for line in data["allocations"]
        ]
        allocation_table = Table(
            [allocation_header] + allocation_rows,
            colWidths=[4 * cm, 5 * cm, 3 * cm, 4 * cm],
        )
        allocation_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ALIGN", (3, 0), (3, -1), "RIGHT"),
        ]))
        elements.append(allocation_table)
    else:
        elements.append(Paragraph("No allocations recorded for this payment.", normal_style))

    elements.append(Spacer(1, 0.5 * cm))
    elements.append(Paragraph(f"Total Allocated: {data['total_allocated']:,.2f}", normal_style))
    elements.append(Paragraph(f"Unallocated Amount: {data['unallocated_amount']:,.2f}", normal_style))

    if data["notes"]:
        elements.append(Spacer(1, 0.5 * cm))
        elements.append(Paragraph(f"Notes: {data['notes']}", normal_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer