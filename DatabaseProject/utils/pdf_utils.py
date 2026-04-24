from reportlab.pdfgen import canvas
import os
from datetime import datetime

def generate_receipt_pdf(order_id, user_name, items, total_amount, masked_card=None):

    receipts_folder = "static/receipts"
    os.makedirs(receipts_folder, exist_ok=True)

    file_path = f"{receipts_folder}/receipt_{order_id}.pdf"
    c = canvas.Canvas(file_path)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, f"Receipt for Order #{order_id}")

    c.setFont("Helvetica", 12)
    c.drawString(50, 780, f"Customer: {user_name}")
    c.drawString(50, 760, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    y = 720
    c.drawString(50, y, "Items:")
    y -= 20

    for item in items:
        c.drawString(50, y, f"{item['title']} x{item['quantity']} — ${item['price']}")
        y -= 20

    # Total section
    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, f"Total Amount: ${total_amount}")
    y -= 20

    # Simulated card info (masked)
    if masked_card:
        c.setFont("Helvetica", 10)
        c.drawString(50, y, f"Payment (Simulated): {masked_card}")
        y -= 20

    # Finish PDF
    c.save()
    return f"receipts/receipt_{order_id}.pdf"
