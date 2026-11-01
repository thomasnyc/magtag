import time
import displayio
from adafruit_magtag.magtag import MagTag

# Pre-encoded QR matrices (ECC Level M) so QR rendering requires no extra libraries or files:
# - GCP_QR_BITS: 37x37 modules -> https://github.com/GoogleCloudPlatform/scientific-computing-examples/tree/main
# - LINKEDIN_QR_BITS: 33x33 modules -> https://www.linkedin.com/in/thomas-leung-9960663/
GCP_QR_SIZE = 37
GCP_QR_CAPTION = "Scientific computing examples"
GCP_QR_BITS = (
    b"\xfe\x34\xe4\x63\xf8\x82\xa9\x8a\x42\x08\xba\xe0\xa6\x2a\xe8\xba\xdc\x40\xda\xe8"
    b"\xba\x7a\xfd\x0a\xe8\x82\x17\xac\xe2\x08\xfe\xaa\xaa\xab\xf8\x00\x8a\x02\x38\x00"
    b"\x82\xad\xc1\xc6\x70\x48\xdc\xb3\x71\xf0\xe7\x8d\xc8\xff\xd8\x61\xa0\x2a\x24\x48"
    b"\x57\xbd\x88\x8b\x48\x88\x89\xfd\x51\x50\xf3\xd9\xc2\x35\xd8\x70\x77\xa1\x1d\x60"
    b"\xe2\x41\x32\xf6\xb0\x89\xae\xff\x59\x30\x9a\x2c\x95\xdc\xa8\x3d\x77\x98\xaf\xc8"
    b"\xb2\x24\x52\xd6\xe0\x08\x59\x53\x34\xa0\x1e\xc1\xc6\x3d\xd8\xb9\x1d\x61\x2f\xd8"
    b"\xae\x45\x58\x13\x08\x88\xd8\x37\x7c\x40\xab\x53\xea\x7f\xf8\xa8\xc0\xa0\x02\xe0"
    b"\x8f\x6d\xcb\xbf\xf0\x00\xa3\xab\x58\x80\xfe\x4d\x7b\x6a\x88\x82\x3f\x89\x18\x98"
    b"\xba\x52\x23\xff\xa0\xba\x5c\x53\x2e\x08\xba\x1c\x0e\x78\x18\x82\x29\x8a\xba\xc8"
    b"\xfe\xf4\xb9\x8f\x48"
)

LINKEDIN_QR_SIZE = 33
LINKEDIN_QR_BITS = (
    b"\xfe\x64\xfd\x3f\x80\x82\x4f\x44\xa0\x80\xba\xed\xfc\x2e\x80\xba\xeb\x9d\xae\x80"
    b"\xba\x95\x23\x2e\x80\x82\xc1\xec\x20\x80\xfe\xaa\xaa\xbf\x80\x00\xe1\x07\x80\x00"
    b"\xbe\x67\xc2\xbe\x00\xd5\xc8\xb1\x37\x80\x13\x19\xa4\xeb\x00\x31\x92\x99\x2f\x00"
    b"\x2b\xe0\x35\x5c\x00\x08\xaf\xc9\xa3\x80\xea\xba\x52\xe5\x00\x18\x4e\x9d\x62\x00"
    b"\x42\xc2\x53\xd8\x80\xb1\x14\x79\xf6\x80\xce\x6f\x4c\x5b\x00\x64\x50\xe1\x7f\x00"
    b"\xf2\xbc\x9e\x0d\x80\xc4\x5b\x63\xa4\x80\xae\x79\x88\x47\x00\x81\xa7\x07\x66\x00"
    b"\x8f\xcf\x63\xf8\x80\x00\xd0\xbd\x8a\x80\xfe\x6b\xa3\xab\x00\x82\x91\x0d\x8f\x80"
    b"\xba\xee\x24\xfd\x80\xba\xcf\xcd\x4c\x80\xba\xda\x57\xf2\x00\x82\x0a\x9e\x8e\x00"
    b"\xfe\x9e\x53\x91\x00"
)

TEXT_WRAP = 28
QR_CAPTION_WRAP = 48
TEXT_MAXLEN = 120
LINE_SPACING = 0.5
POLL_INTERVAL = 0.05
DEBOUNCE_DELAY = 0.15

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
    (50, 0.5, 1, QR_CAPTION_WRAP),
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
display = magtag.graphics.display
display_width = display.width
display_height = display.height
center_x = display_width // 2
center_y = display_height // 2


def get_root_group():
    """Return the active displayio root group across CircuitPython versions."""
    for obj, attr in (
        (magtag, "splash"),
        (magtag.graphics, "splash"),
        (magtag.graphics, "root_group"),
        (display, "root_group"),
    ):
        group = getattr(obj, attr, None)
        if group is not None:
            return group
    raise RuntimeError("Display root group not found")


def build_qr_group(matrix_size, packed_bits, scale, border=2, y_pos=None):
    """Build a centered displayio.Group containing a crisp 2-color QR bitmap."""
    bmp_size = matrix_size + 2 * border
    bitmap = displayio.Bitmap(bmp_size, bmp_size, 2)
    row_bytes = (matrix_size + 7) // 8

    for y in range(matrix_size):
        row_offset = y * row_bytes
        for x in range(matrix_size):
            if packed_bits[row_offset + (x >> 3)] & (0x80 >> (x & 7)):
                bitmap[x + border, y + border] = 1

    palette = displayio.Palette(2)
    palette[0] = 0xFFFFFF
    palette[1] = 0x000000

    pixel_size = bmp_size * scale
    x_pos = (display_width - pixel_size) // 2
    if y_pos is None:
        y_pos = (display_height - pixel_size) // 2

    tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
    group = displayio.Group(scale=scale, x=x_pos, y=y_pos)
    group.append(tile_grid)
    return group


root_group = get_root_group()

for y_offset, anchor_y, scale, wrap in TEXT_LAYOUTS:
    magtag.add_text(
        text_wrap=wrap,
        text_maxlen=TEXT_MAXLEN,
        text_position=(center_x, center_y + y_offset),
        line_spacing=LINE_SPACING,
        text_anchor_point=(0.5, anchor_y),
        text_scale=scale,
    )

# Pre-build both QR groups once (zero external library or file dependencies)
gcp_qr_group = build_qr_group(GCP_QR_SIZE, GCP_QR_BITS, scale=2, border=3, y_pos=8)
linkedin_qr_group = build_qr_group(LINKEDIN_QR_SIZE, LINKEDIN_QR_BITS, scale=3, border=2)

active_qr_group = None
current_view = None


def safe_refresh():
    """Wait until the e-ink display is ready and perform a guaranteed refresh."""
    for _ in range(30):
        while getattr(display, "busy", False):
            time.sleep(0.05)
        wait = display.time_to_refresh
        if wait > 0:
            time.sleep(wait + 0.1)
        try:
            display.refresh()
            return
        except RuntimeError:
            time.sleep(0.25)


def wait_for_release(button_attr):
    """Wait until the pressed button is released and debounce switch bounce."""
    while getattr(magtag.peripherals, button_attr):
        time.sleep(POLL_INTERVAL)
    time.sleep(DEBOUNCE_DELAY)


def clear_qr():
    """Remove any currently displayed QR code group from the root group."""
    global active_qr_group
    if active_qr_group is not None:
        try:
            root_group.remove(active_qr_group)
        except ValueError:
            pass
        active_qr_group = None


def show_card(lines, slot_offset, view):
    """Display a 3-line text card and hide any active QR code."""
    global current_view
    clear_qr()

    active_slots = range(slot_offset, slot_offset + len(lines))
    for slot in range(len(TEXT_LAYOUTS)):
        if slot not in active_slots:
            magtag.set_text(" ", slot, False)

    for i, text in enumerate(lines):
        magtag.set_text(text, slot_offset + i, False)

    safe_refresh()
    current_view = view


def show_qr(qr_group, view, caption=None):
    """Clear card text slots, attach the QR bitmap group, and refresh the display."""
    global active_qr_group, current_view
    clear_qr()

    for slot in range(len(TEXT_LAYOUTS)):
        if slot != QR_CAPTION_SLOT:
            magtag.set_text(" ", slot, False)
    magtag.set_text(caption if caption else " ", QR_CAPTION_SLOT, False)

    root_group.append(qr_group)
    active_qr_group = qr_group

    safe_refresh()
    current_view = view


show_card(BADGE_LINES, BADGE_SLOT_OFFSET, VIEW_BADGE)

while True:
    if magtag.peripherals.button_a_pressed:
        if current_view == VIEW_GCP_QR:
            show_card(BADGE_LINES, BADGE_SLOT_OFFSET, VIEW_BADGE)
        else:
            show_qr(gcp_qr_group, VIEW_GCP_QR, caption=GCP_QR_CAPTION)
        wait_for_release("button_a_pressed")

    elif magtag.peripherals.button_b_pressed:
        if current_view == VIEW_WORK_CONTACT:
            show_qr(linkedin_qr_group, VIEW_LINKEDIN_QR)
        else:
            show_card(WORK_CONTACT_LINES, CONTACT_SLOT_OFFSET, VIEW_WORK_CONTACT)
        wait_for_release("button_b_pressed")

    elif magtag.peripherals.button_c_pressed:
        show_card(PERSONAL_CONTACT_LINES, CONTACT_SLOT_OFFSET, VIEW_PERSONAL_CONTACT)
        wait_for_release("button_c_pressed")

    time.sleep(POLL_INTERVAL)
