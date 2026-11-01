import time
from adafruit_magtag.magtag import MagTag

GCP_QR_URL = "https://github.com/GoogleCloudPlatform/scientific-computing-examples/tree/main"
GCP_QR_CAPTION = "Scientific computing examples"
LINKEDIN_QR_URL = "https://www.linkedin.com/in/thomas-leung-9960663/"

QR_SIZE = 2
QR_OFFSET = 45
QR_CAPTIONED_Y_OFFSET = -56

TEXT_WRAP = 28
QR_CAPTION_WRAP = 48
TEXT_MAXLEN = 120
LINE_SPACING = 0.5
POLL_INTERVAL = 0.05
REFRESH_POLL_INTERVAL = 0.1

BADGE_SLOT_OFFSET = 0
CONTACT_SLOT_OFFSET = 3
QR_CAPTION_SLOT = 6

VIEW_BADGE = "badge"
VIEW_GCP_QR = "gcp_qr"
VIEW_WORK_CONTACT = "work_contact"
VIEW_LINKEDIN_QR = "linkedin_qr"
VIEW_PERSONAL_CONTACT = "personal_contact"

# (y_offset_from_center, anchor_y, text_scale, text_wrap)
TEXT_LAYOUTS = (
    # Slots 0-2: Main badge view
    (-10, 0.8, 7, TEXT_WRAP),
    (-2, 0.05, 2, TEXT_WRAP),
    (25, 0.05, 3, TEXT_WRAP),
    # Slots 3-5: Contact card views
    (-10, 0.8, 4, TEXT_WRAP),
    (-2, 0.05, 2, TEXT_WRAP),
    (25, 0.05, 2, TEXT_WRAP),
    # Slot 6: QR code caption
    (49, 0.5, 1, QR_CAPTION_WRAP),
)

BADGE_LINES = (
    "Thomas",
    "HPC Troublemaker",
    "Google Cloud",
)

WORK_CONTACT_LINES = (
    "Thomas Leung",
    "646-946-9664",
    "thomashk@google.com",
)

PERSONAL_CONTACT_LINES = (
    "Thomas Leung",
    "973-997-6789",
    "thomashk@thomashk.com",
)

magtag = MagTag()
showing_qr = False
current_view = None

center_x = magtag.graphics.display.width // 2
center_y = magtag.graphics.display.height // 2

for y_offset, anchor_y, scale, wrap in TEXT_LAYOUTS:
    magtag.add_text(
        text_wrap=wrap,
        text_maxlen=TEXT_MAXLEN,
        text_position=(center_x, center_y + y_offset),
        line_spacing=LINE_SPACING,
        text_anchor_point=(0.5, anchor_y),
        text_scale=scale,
    )


def wait_for_display():
    """Wait until the e-ink display is ready to refresh."""
    while magtag.graphics.display.time_to_refresh > 0:
        time.sleep(REFRESH_POLL_INTERVAL)


def wait_for_release(button_attr):
    """Wait until the pressed button is released."""
    while getattr(magtag.peripherals, button_attr):
        time.sleep(POLL_INTERVAL)


def clear_qr():
    """Remove any active QR code without triggering an extra refresh."""
    global showing_qr
    if showing_qr:
        magtag.graphics._auto_refresh = False
        magtag.graphics.qrcode(None)
        magtag.graphics._auto_refresh = True
        showing_qr = False


def show_card(lines, slot_offset, view):
    """Display a 3-line text card and hide any active QR code."""
    global current_view
    wait_for_display()
    clear_qr()

    active_slots = range(slot_offset, slot_offset + len(lines))
    for slot in range(len(TEXT_LAYOUTS)):
        if slot not in active_slots:
            magtag.set_text(" ", slot, False)

    last_index = len(lines) - 1
    for i, text in enumerate(lines):
        magtag.set_text(text, slot_offset + i, i == last_index)

    current_view = view


def show_qr(url, view, caption=None):
    """Clear card text slots and render a QR code with an optional caption."""
    global showing_qr, current_view
    wait_for_display()
    clear_qr()

    for slot in range(len(TEXT_LAYOUTS)):
        if slot != QR_CAPTION_SLOT:
            magtag.set_text(" ", slot, False)
    magtag.set_text(caption if caption else " ", QR_CAPTION_SLOT, False)

    y_offset = QR_CAPTIONED_Y_OFFSET if caption else -QR_OFFSET
    magtag.graphics.qrcode(
        url,
        qr_size=QR_SIZE,
        x=center_x - QR_OFFSET,
        y=center_y + y_offset,
    )
    showing_qr = True
    current_view = view


show_card(BADGE_LINES, BADGE_SLOT_OFFSET, VIEW_BADGE)

while True:
    if magtag.peripherals.button_a_pressed:
        if current_view == VIEW_GCP_QR:
            show_card(BADGE_LINES, BADGE_SLOT_OFFSET, VIEW_BADGE)
        else:
            show_qr(GCP_QR_URL, VIEW_GCP_QR, caption=GCP_QR_CAPTION)
        wait_for_release("button_a_pressed")

    elif magtag.peripherals.button_b_pressed:
        if current_view == VIEW_WORK_CONTACT:
            show_qr(LINKEDIN_QR_URL, VIEW_LINKEDIN_QR)
        else:
            show_card(WORK_CONTACT_LINES, CONTACT_SLOT_OFFSET, VIEW_WORK_CONTACT)
        wait_for_release("button_b_pressed")

    elif magtag.peripherals.button_c_pressed:
        show_card(PERSONAL_CONTACT_LINES, CONTACT_SLOT_OFFSET, VIEW_PERSONAL_CONTACT)
        wait_for_release("button_c_pressed")

    time.sleep(POLL_INTERVAL)
