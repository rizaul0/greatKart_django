from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import black, HexColor
from reportlab.pdfgen import canvas
from io import BytesIO
from decimal import Decimal
import hashlib
PRIMARY = HexColor("#2f4f6f")

def generate_invoice_pdf(order, order_products):
    buffer = BytesIO()

    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50

    # ================= HEADER =================
    p.setFont("Helvetica-Bold", 22)
    p.setFillColor(PRIMARY)
    p.drawString(40, y, "GreatKart")
    p.drawRightString(width - 40, y, "INVOICE")
    y -= 20
    p.setFont("Helvetica-Bold", 10)
    p.drawString(40, y, "Payment Method:")
    p.setFont("Helvetica", 10)
    p.drawString(160, y, order.payment_method)

    y -= 40
    p.setFont("Helvetica", 10)
    p.setFillColor(black)
    p.drawString(40, y, f"Invoice No: {order.order_number}")
    p.drawString(40, y - 15, f"Date: {order.created_at.strftime('%d %b %Y')}")

    y -= 30
    p.line(40, y, width - 40, y)

    # ================= BILLING =================
    y -= 25
    p.setFont("Helvetica-Bold", 11)
    p.drawString(40, y, "Bill From:")
    p.drawString(width / 2 + 20, y, "Bill To:")

    y -= 15
    p.setFont("Helvetica", 10)
    p.drawString(40, y, "GreatKart Pvt Ltd")
    p.drawString(width / 2 + 20, y, f"{order.user.first_name} {order.user.last_name}")

    y -= 15
    p.drawString(40, y, "India")
    p.drawString(width / 2 + 20, y, order.user.email)

    y -= 30
    p.line(40, y, width - 40, y)

    # ================= TABLE HEADER =================
    y -= 20
    p.setFont("Helvetica-Bold", 10)
    p.drawString(40, y, "Product (Color / Size)")
    p.drawString(300, y, "Qty")
    p.drawString(350, y, "Price")
    p.drawString(440, y, "Total")

    y -= 10
    p.line(40, y, width - 40, y)

    # ================= TABLE ROWS =================
    p.setFont("Helvetica", 10)
    subtotal = Decimal('0.00')

    for item in order_products:
        y -= 18

        # 🔹 Build variant text (Color + Size)
        variant_text = ""
        if item.color or item.size:
           variant_text = f" ({item.color} / {item.size})"

        product_text = f"{item.product.product_name}{variant_text}"

        line_total = Decimal(item.quantity) * Decimal(str(item.product_price))

        subtotal += line_total

        p.drawString(40, y, product_text)
        p.drawString(300, y, str(item.quantity))
        p.drawRightString(420, y, f"Rs. {item.product_price:.2f}")
        p.drawRightString(width - 40, y, f"Rs. {line_total:.2f}")

        if y < 100:
            p.showPage()
            p.setFont("Helvetica", 10)
            y = height - 50

    # ================= SUMMARY =================
    y -= 30
    p.line(300, y, width - 40, y)

    y -= 20
    p.drawString(300, y, "Subtotal:")
    p.drawRightString(width - 40, y, f"Rs. {subtotal:.2f}")

    # 🔹 DISCOUNT (if any)
    discount = (subtotal + order.tax) - order.order_total

    if discount > 0:
        y -= 15
        p.setFillColor(HexColor("#d9534f"))
        p.drawString(300, y, "Discount:")
        p.drawRightString(width - 40, y, f"- Rs. {discount:.2f}")
        p.setFillColor(black)

    y -= 15
    p.drawString(300, y, "Tax (9%):")
    p.drawRightString(width - 40, y, f"Rs. {order.tax:.2f}")

    y -= 20
    p.setFont("Helvetica-Bold", 12)
    p.setFillColor(PRIMARY)
    p.drawString(300, y, "Grand Total:")
    p.drawRightString(width - 40, y, f"Rs. {order.order_total:.2f}")

    # ================= FOOTER =================
    y -= 40
    p.setFont("Helvetica", 9)
    p.setFillColor(black)
    p.drawString(40, y, "Thank you for shopping with GreatKart.")
    p.drawString(40, y - 15, "This is a computer-generated invoice.")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer



def generate_payu_hash(data, salt):
    hash_string = (
        f"{data['key']}|"
        f"{data['txnid']}|"
        f"{data['amount']}|"
        f"{data['productinfo']}|"
        f"{data['firstname']}|"
        f"{data['email']}|"
        f"{data.get('udf1','')}|"
        f"{data.get('udf2','')}|"
        f"{data.get('udf3','')}|"
        f"{data.get('udf4','')}|"
        f"{data.get('udf5','')}||||||{salt}"
    )

    # DEBUG — remove after success
    # print("PAYU HASH STRING (FIXED):", hash_string)

    return hashlib.sha512(hash_string.encode("utf-8")).hexdigest().lower()
