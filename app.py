import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import CircleModuleDrawer, RoundedModuleDrawer
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
import io

# የገጹ አቀማመጥ (Wide layout)
st.set_page_config(page_title="QR Code Generator", layout="wide")

# ----------------- 🔒 የፓስዎርድ ጥበቃ ክፍል (Password Protection: 000000) -----------------
def check_password():
    def password_entered():
        if st.session_state["password"] == "000000":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.subheader("🔐 ግላዊ መግቢያ (Private Access)")
        st.text_input(
            "እባክዎ የመክፈቻ ፓስዎርድ ያስገቡ:", type="password", on_change=password_entered, key="password"
        )
        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("😕 ያስገቡት ፓስዎርድ ስህተት ነው። እባክዎ እንደገና ይሞክሩ።")
        return False
    elif not st.session_state["password_correct"]:
        st.subheader("🔐 ግላዊ መግቢያ (Private Access)")
        st.text_input(
            "እባክዎ የመክፈቻ ፓስዎርድ ያስገቡ:", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 ያስገቡት ፓስዎርድ ስህተት ነው። እባክዎ እንደገና ይሞክሩ።")
        return False
    else:
        return True

if not check_password():
    st.stop()

# ----------------- ዋናው አፕሊኬሽን -----------------
st.title("🖨️ የጉዞ ኬስ ኪውአር ኮድ ማመንጫ (QR Code Generator)")

# ----------------- ግራ በኩል: መረጃ ማስገቢያ (Sidebar) -----------------
st.sidebar.header("📝 መረጃዎችን ማስገቢያ")

destination_country = st.sidebar.text_input("Destination Country", "destination country")
full_name = st.sidebar.text_input("Full Name", "full name")
labor_id = st.sidebar.text_input("Labor ID (Value)", "labor id")
ticket_reservation = st.sidebar.text_input("Ticket Reservation (QR ውስጥ ብቻ)", "ticket")

# ----------------- ቀኝ በኩል: ፕሪቪው እና አውትፑት (Main Content) -----------------

qr_data = f'{{"key":"LABOR_ID","value":"{labor_id}","phone_number":"","ticket_res":"{ticket_reservation}"}}'

# የ QR ኮድ ማመንጨት (Version 2 እና ክብ ማዕዘኖች/ነጠብጣቦች)
qr = qrcode.QRCode(
    version=2,
    error_correction=qrcode.constants.ERROR_CORRECT_M,
    box_size=10,
    border=2,
)
qr.add_data(qr_data)
qr.make(fit=True)

try:
    qr_img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=CircleModuleDrawer(),
        eye_drawer=RoundedModuleDrawer(),
        fill_color="black",
        back_color="white"
    ).convert('RGB')
except Exception:
    qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

# ሎጎ ማካተት
try:
    logo_path = "logo.png" 
    logo = Image.open(logo_path)
    basewidth = 50
    wpercent = (basewidth / float(logo.size[0]))
    hsize = int(float(logo.size[1]) * float(wpercent))
    logo = logo.resize((basewidth, hsize), Image.Resampling.LANCZOS)
    pos = ((qr_img.size[0] - logo.size[0]) // 2, (qr_img.size[1] - logo.size[1]) // 2)
    qr_img.paste(logo, pos)
except Exception:
    draw = ImageDraw.Draw(qr_img)
    center_x, center_y = qr_img.size[0] // 2, qr_img.size[1] // 2
    box_size = 35
    draw.rectangle(
        [center_x - box_size, center_y - box_size, center_x + box_size, center_y + box_size],
        fill="blue"
    )

# የካርዱ ምስል ማዘጋጀት
card_width = 500
card_height = 650
card_img = Image.new("RGB", (card_width, card_height), "white")
draw_card = ImageDraw.Draw(card_img)

try:
    font = ImageFont.truetype("/Library/Fonts/Arial Bold.ttf", 15)
except Exception:
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica Bold.ttc", 15)
    except Exception:
        font = ImageFont.load_default()

def draw_centered_text(draw, box, text, font):
    x1, y1, x2, y2 = box
    box_width = x2 - x1
    box_height = y2 - y1
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = x1 + (box_width - text_width) / 2
    text_y = y1 + (box_height - text_height) / 2 - 2
    draw.text((text_x, text_y), text, fill="black", font=font)

# ሳጥኖች እና ጽሁፎች
box_country = [50, 40, 450, 95]
draw_card.rounded_rectangle(box_country, radius=10, outline="black", width=2)
text_1 = f"Destination Country - {destination_country}"
draw_centered_text(draw_card, box_country, text_1, font)

qr_resized = qr_img.resize((280, 280))
card_img.paste(qr_resized, (110, 120))

box_name = [50, 430, 450, 485]
draw_card.rounded_rectangle(box_name, radius=10, outline="black", width=2)
draw_centered_text(draw_card, box_name, full_name, font)

box_id = [50, 500, 450, 555]
draw_card.rounded_rectangle(box_id, radius=10, outline="black", width=2)
text_id = f"Labor ID: {labor_id}"
draw_centered_text(draw_card, box_id, text_id, font)

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 🖼️ የካርዱ ፕሪቪው (Preview)")
    st.image(card_img, width=380)
    
    buf = io.BytesIO()
    card_img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    
    st.download_button(
        label="📥 QR ካርዱን አውርድ (Download PNG)",
        data=byte_im,
        file_name=f"QR_{labor_id}.png",
        mime="image/png"
    )

with col2:
    st.markdown("### 📌 የQR ኮድ ውስጥ የሚከተተው ትክክለኛ መረጃ (Payload):")
    st.code(qr_data)