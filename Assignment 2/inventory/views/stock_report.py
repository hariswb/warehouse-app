from datetime import datetime
from dataclasses import dataclass, asdict
from collections import defaultdict
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from django.http import HttpResponse

from ..models.item import Item
from ..models.purchase import PurchaseDetail
from ..models.sell import SellDetail

from reportlab.lib.pagesizes import A3
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from io import BytesIO


@dataclass
class Transaction:
    date: str
    code: str
    description: str
    in_qty: int = 0
    in_price: int = 0
    in_total: int = 0
    out_qty: int = 0
    out_price: int = 0
    out_total: int = 0
    type: str = ""
    stock_qty: list = None
    stock_price: list = None
    stock_total: list = None
    balance_qty: int = 0
    balance: int = 0

class StockReportView(APIView):
    def get(self, request, item_code):
        start = parse_date(request.GET.get("start_date"))
        end = parse_date(request.GET.get("end_date"))
        is_pdf = request.GET.get("pdf") == "true"

        print(item_code)
        item = get_object_or_404(Item, code=item_code, is_deleted=False)

        purchases = PurchaseDetail.objects.filter(
            item=item, header__date__range=(start, end), is_deleted=False
        ).select_related("header")

        print(purchases)

        sells = SellDetail.objects.filter(
            item=item, header__date__range=(start, end), is_deleted=False
        ).select_related("header")

        transactions = map_transactions(purchases, sells)
        processed = apply_fifo(transactions)

        if is_pdf:
            return self.generate_pdf(processed, item, start, end)

        return Response(serialize_report(processed, item))
    
    def generate_pdf(self, transactions, item, start, end):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A3, rightMargin=20, leftMargin=20, topMargin=40, bottomMargin=30)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        title_style = ParagraphStyle(name="TitleStyle", parent=styles["Title"], alignment=1)
        subtitle_style = ParagraphStyle(name="SubTitleStyle", parent=styles["Normal"], alignment=0)

        elements.append(Paragraph(f"Stock Report", title_style))
        elements.append(Paragraph(f"Items code : {item.code}", subtitle_style))
        elements.append(Paragraph(f"Name : {item.name}", subtitle_style))
        elements.append(Paragraph("Unit : Pcs", subtitle_style))
        elements.append(Spacer(1, 12))

        # Header row 1
        header_row1 = [
            "No", "Date", "Description", "Code",
            "In", "", "", "Out", "", "", "Stock", "", ""
        ]

        # Header row 2 (sub-columns)
        header_row2 = [
            "", "", "", "",
            "Qty", "Price", "Total",
            "Qty", "Price", "Total",
            "Qty", "Price", "Total"
        ]

        data = [header_row1, header_row2]
        style_data = []

        # Data rows
        for idx, t in enumerate(transactions, start=1):
            data.append([
                idx,
                t.date,
                t.description,
                t.code,
                '{:.0f}'.format(t.in_qty or 0),
                '{:.0f}'.format(t.in_price or 0),
                '{:.0f}'.format(t.in_total or 0),
                '{:.0f}'.format(t.out_qty or 0),
                '{:.0f}'.format(t.out_price or 0),
                '{:.0f}'.format(t.out_total or 0),
                '{:.0f}'.format(t.stock_qty or 0),
                '{:.0f}'.format(t.stock_price or 0),
                '{:.0f}'.format(t.stock_total or 0),
            ])

            data.append([
                "Balance", "", "", "", "",
                "","", "", "", "", 
                '{:.0f}'.format(t.balance_qty or 0),
                '{:.0f}'.format(t.balance or 0), ""
            ])

            # Add style for balance row
            style_data += [
                ("SPAN", (0, idx*2+1),(9, idx*2+1)),
                ("SPAN", (11, idx*2+1),(12, idx*2+1)),
            ]

        summary = [
            "Summary", "", "", "",
            sum(t.in_qty for t in transactions), "","",
            sum(t.out_qty for t in transactions), "", "", 
            t.balance_qty or 0, '{:.0f}'.format(t.balance or 0), ""
        ]
        data.append(summary)
        # Style data for summary
        style_data += [
            ("SPAN", (0, len(transactions)*2+2), (9, len(transactions)*2+2)),
            ("SPAN", (11, len(transactions)*2+2), (12, len(transactions)*2+2)),
        ]

        # Table & styling
        col_widths = [30, 60, 110, 60, 40, 60, 70, 40, 60, 70, 70, 70, 70]
        table = Table(data, colWidths=col_widths, repeatRows=2)

        style = TableStyle(style_data + [
            # General
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 1), "Helvetica-Bold"),
            ("BACKGROUND", (0, 0), (-1, 1), colors.HexColor("#d9e1f2")),
            ("ALIGN", (0, 0), (-1, 1), "CENTER"),

            # Alignment of numeric cells
            ("ALIGN", (4, 2), (-1, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

            # Padding
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),

            # Merge header groups
            ("SPAN", (4, 0), (6, 0)),  # In
            ("SPAN", (7, 0), (9, 0)),  # Out
            ("SPAN", (10, 0), (12, 0)),  # Stock

            # Merge individual header cells
            ("SPAN", (0, 0), (0, 1)),  # No
            ("SPAN", (1, 0), (1, 1)),  # Date
            ("SPAN", (2, 0), (2, 1)),  # Description
            ("SPAN", (3, 0), (3, 1)),  # Code
        ])

        table.setStyle(style)
        elements.append(table)
        doc.build(elements)
        buffer.seek(0)
        return HttpResponse(buffer, content_type="application/pdf")

def map_transactions(purchases, sells):
    transactions = []
    for pd in purchases:
        t = Transaction(
            date=pd.header.date.strftime("%d-%m-%Y"),
            description=pd.header.description,
            code=pd.header.code,
            in_qty=pd.quantity,
            in_price=pd.unit_price,
            in_total=pd.quantity * pd.unit_price,
            type="in",
        )
        transactions.append(t)

    for sd in sells:
        t = Transaction(
            date=sd.header.date.strftime("%d-%m-%Y"),
            description=sd.header.description,
            code=sd.header.code,
            out_qty=sd.quantity,
            out_price=0,  # will be calculated via FIFO
            out_total=0,
            type="out",
        )
        transactions.append(t)

    return sorted(transactions, key=lambda x: (datetime.strptime(x.date, "%d-%m-%Y"), x.code))

def apply_fifo(transactions):
    stock = []
    results = []

    for t in transactions:
        if t.type == "in":
            stock.append([t.in_qty, t.in_price])
        else:
            qty_needed = t.out_qty
            total_out = 0
            new_stock = []

            for qty, price in stock:
                if qty_needed == 0:
                    new_stock.append([qty, price])
                    continue

                if qty <= qty_needed:
                    total_out += qty * price
                    qty_needed -= qty
                else:
                    total_out += qty_needed * price
                    new_stock.append([qty - qty_needed, price])
                    qty_needed = 0

            t.out_total = total_out
            t.out_price = total_out // t.out_qty if t.out_qty else 0
            stock = new_stock

        t.stock_qty = sum([q for q, _ in stock])
        t.stock_price = sum([p for _, p in stock])
        t.stock_total = sum([q * p for q, p in stock])
        t.balance_qty = sum(q for q, _ in stock)
        t.balance = sum(q * p for q, p in stock)
        results.append(t)

    return results

def serialize_report(transactions, item):
    return {
        "result": {
            "item_code": item.code,
            "name": item.name,
            "unit": item.unit,
            "items": [asdict(t) for t in transactions],
            "summary": {
                "in_qty": sum(t.in_qty for t in transactions),
                "out_qty": sum(t.out_qty for t in transactions),
                "balance_qty": transactions[-1].balance_qty if transactions else 0,
                "balance": transactions[-1].balance if transactions else 0,
            },
        }
    }


