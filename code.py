import time
import displayio
from adafruit_magtag.magtag import MagTag

# Pre-encoded QR matrices (ECC Level M) so QR rendering requires no extra libraries or files:
# - GCP_QR_BITS: 37x37 modules -> https://github.com/GoogleCloudPlatform/scientific-computing-examples/tree/main
# - LINKEDIN_QR_BITS: 33x33 modules -> https://www.linkedin.com/in/thomas-leung-9960663/
# - PERSONAL_VCARD_QR_BITS: 45x45 modules -> vCard 3.0 (Thomas Leung, 973-997-6789, thomashk@thomashk.com)
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

PERSONAL_VCARD_QR_SIZE = 45
PERSONAL_VCARD_QR_BITS = (
    b"\xfe\x3d\xc0\xb4\x8b\xf8\x82\x7a\x43\x87\x52\x08\xba\xcc\x9c\x31\x12\xe8\xba\xa8"
    b"\xcc\x23\x9a\xe8\xba\xd9\x7f\xb6\xba\xe8\x82\xbf\xa8\xd1\x42\x08\xfe\xaa\xaa\xaa"
    b"\xab\xf8\x00\xa9\x68\xd4\x48\x00\xbe\x6f\xbf\x91\xdb\xe0\xa8\x47\xff\x15\x0e\x90"
    b"\xb7\x60\x64\xa2\xd7\xb8\xac\x5f\x59\xe4\xf0\x78\x02\xd8\x2b\x11\x6e\x98\x9c\xf4"
    b"\xd9\xc4\x09\x30\x2b\xf5\x14\x27\x57\xb8\xed\xc4\xdc\x20\x83\x68\xfe\x73\x64\xb5"
    b"\x4b\xb0\xa1\xce\xe2\x3e\x69\x30\x12\xff\x85\xda\x1b\x30\xe0\x51\x90\x7c\x18\xd0"
    b"\xff\xae\xdf\xd5\xef\xe8\x88\xa8\xa8\xce\x28\xe8\xea\xa0\x5a\xb1\x9a\xf0\xd8\xeb"
    b"\x08\xf1\xd8\xc0\x5f\xee\xcf\x88\x6f\xb0\x1c\xc2\xbf\x1b\xf8\x50\x6f\x3b\x2f\x16"
    b"\x56\x48\x35\x43\x2e\xc1\x05\x70\x33\x1e\x68\x59\x7b\x90\xf1\x73\x21\x52\x8c\xe8"
    b"\x13\x0d\xc9\xf6\xd6\x78\xc1\x27\xa5\x2a\xbc\xa8\x86\x3f\xcb\xb1\x23\xc0\xc5\xc0"
    b"\x4e\x31\x9e\xf0\x0a\xd2\x53\x9b\x31\x10\x78\xa6\xc6\x2d\x5f\x00\x9a\x17\x1f\xe7"
    b"\x4f\xb0\x00\xa7\xa8\xe6\xb8\xf0\xfe\x51\x2a\xf1\x0a\xf0\x82\xf4\xf8\xb8\xf8\xb8"
    b"\xba\x81\x4f\xaf\xdf\xa8\xba\x9c\x82\x5b\xdb\xc0\xba\xf7\x34\x80\x13\x60\x82\x04"
    b"\x98\x57\xa4\x68\xfe\xab\x91\xc2\x76\x80"
)

# 24x48 4-shade grayscale HPC Server Rack pixel art (2 bits/pixel -> 288 bytes, scaled 2x -> 48x96 px)
RACK_WIDTH = 24
RACK_HEIGHT = 48
RACK_BITS = (
    b"\x3f\xff\xff\xff\xff\xfc\xff\xff\xff\xff\xff\xff\xf5\x55\x55\x55\x55\x5f"
    b"\xf6\xaa\xaa\xaa\xaa\x9f\xf6\x08\x20\x80\x4c\x9f\xf6\x08\x20\x80\x0c\x9f"
    b"\xf6\xaa\xaa\xaa\xaa\x9f\xf5\x55\x55\x55\x55\x5f\xf6\xaa\xaa\xaa\xaa\x9f"
    b"\xf6\x08\x20\x80\x4c\x9f\xf6\x08\x20\x80\x0c\x9f\xf6\xaa\xaa\xaa\xaa\x9f"
    b"\xf5\x55\x55\x55\x55\x5f\xf6\xaa\xaa\xaa\xaa\x9f\xf6\x08\x20\x80\x4c\x9f"
    b"\xf6\x08\x20\x80\x0c\x9f\xf6\xaa\xaa\xaa\xaa\x9f\xf5\x55\x55\x55\x55\x5f"
    b"\xf6\xaa\xaa\xaa\xaa\x9f\xf6\x3c\xf3\xc0\x4c\x9f\xf6\x3c\xf3\xc0\x4c\x9f"
    b"\xf6\x3c\xf3\xc0\x00\x9f\xf6\xaa\xaa\xaa\xaa\x9f\xf5\x55\x55\x55\x55\x5f"
    b"\xf6\xaa\xaa\xaa\xaa\x9f\xf6\x33\x33\x30\x40\x9f\xf6\x11\x11\x10\xc0\x9f"
    b"\xf6\xaa\xaa\xaa\xaa\x9f\xf5\x55\x55\x55\x55\x5f\xf6\xaa\xaa\xaa\xaa\x9f"
    b"\xf6\x3c\xf3\xcf\x0c\x9f\xf6\x3c\xf3\xcf\x04\x9f\xf6\x3c\xf3\xcf\x0c\x9f"
    b"\xf6\x3c\xf3\xcf\x00\x9f\xf6\x3c\xf3\xcf\x0c\x9f\xf6\xaa\xaa\xaa\xaa\x9f"
    b"\xf5\x55\x55\x55\x55\x5f\xf6\xaa\xaa\xaa\xaa\x9f\xf6\x00\x00\x00\x00\x9f"
    b"\xf6\x2a\xaa\xaa\xa8\x9f\xf6\x00\x00\x00\x00\x9f\xf6\x2a\xaa\xaa\xa8\x9f"
    b"\xf6\xaa\xaa\xaa\xaa\x9f\xf5\x55\x55\x55\x55\x5f\xff\xff\xff\xff\xff\xff"
    b"\x3f\xff\xff\xff\xff\xfc\x0f\xf0\x00\x00\x0f\xf0\x0f\xf0\x00\x00\x0f\xf0"
)

# Google's 4 colors balanced for RGB NeoPixels: Blue, Red, Yellow, Green
GOOGLE_COLORS = (
    (0, 70, 255),
    (255, 15, 0),
    (255, 150, 0),
    (0, 200, 25),
)
LIGHT_SHOW_BRIGHTNESS = 0.25
LIGHT_SHOW_SPEED = 1.4  # Color wave cycles per second
TELEMETRY_DURATION = 120.0  # 2 minutes before returning to default badge

TEXT_WRAP = 28
QR_CAPTION_WRAP = 48
TEXT_MAXLEN = 48
LINE_SPACING = 0.5
POLL_INTERVAL = 0.05
DEBOUNCE_DELAY = 0.15

BADGE_SLOT_OFFSET = 0
CONTACT_SLOT_OFFSET = 3
QR_CAPTION_SLOT = 6
TELEMETRY_SLOT_OFFSET = 7

TELEMETRY_TEXT_X = 61
ENERGY_BAR_WIDTH = 228
ENERGY_BAR_HEIGHT = 10

VIEW_BADGE = "badge"
VIEW_GCP_QR = "gcp_qr"
VIEW_WORK_CONTACT = "work_contact"
VIEW_LINKEDIN_QR = "linkedin_qr"
VIEW_PERSONAL_CONTACT = "personal_contact"
VIEW_PERSONAL_VCARD_QR = "personal_vcard_qr"
VIEW_TELEMETRY = "telemetry"

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

# Ensure NeoPixels start powered off to save battery
magtag.peripherals.neopixel_disable = True

# (x_pos, y_pos, anchor_x, anchor_y, text_scale, text_wrap)
TEXT_LAYOUTS = (
    # Slots 0-2: Main badge view (centered)
    (center_x, center_y - 10, 0.5, 0.8, 7, TEXT_WRAP),
    (center_x, center_y - 2, 0.5, 0.05, 2, TEXT_WRAP),
    (center_x, center_y + 25, 0.5, 0.05, 3, TEXT_WRAP),
    # Slots 3-5: Contact card views (centered)
    (center_x, center_y - 10, 0.5, 0.8, 4, TEXT_WRAP),
    (center_x, center_y - 2, 0.5, 0.05, 2, TEXT_WRAP),
    (center_x, center_y + 25, 0.5, 0.05, 2, TEXT_WRAP),
    # Slot 6: QR code caption (centered)
    (center_x, center_y + 50, 0.5, 0.5, 1, QR_CAPTION_WRAP),
    # Slots 7-9: Server Rack + Live Node Telemetry view (left-aligned next to rack)
    (TELEMETRY_TEXT_X, 25, 0.0, 0.5, 2, 0),
    (TELEMETRY_TEXT_X, 52, 0.0, 0.5, 2, 0),
    (TELEMETRY_TEXT_X, 87, 0.0, 0.5, 1, 0),
)


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


def build_telemetry_group():
    """Build the 4-grayscale pixel-art HPC server rack, divider, and energy bar."""
    palette4 = displayio.Palette(4)
    palette4[0] = 0xFFFFFF  # White
    palette4[1] = 0xAAAAAA  # Light gray
    palette4[2] = 0x555555  # Dark gray
    palette4[3] = 0x000000  # Black

    # 1. Server rack icon (24x48 scaled 2x -> 48x96 at x=6, y=16)
    rack_bmp = displayio.Bitmap(RACK_WIDTH, RACK_HEIGHT, 4)
    bytes_per_row = RACK_WIDTH // 4
    for y in range(RACK_HEIGHT):
        row_offset = y * bytes_per_row
        for byte_i in range(bytes_per_row):
            bval = RACK_BITS[row_offset + byte_i]
            base_x = byte_i * 4
            rack_bmp[base_x, y] = (bval >> 6) & 0x03
            rack_bmp[base_x + 1, y] = (bval >> 4) & 0x03
            rack_bmp[base_x + 2, y] = (bval >> 2) & 0x03
            rack_bmp[base_x + 3, y] = bval & 0x03

    rack_group = displayio.Group(scale=2, x=6, y=16)
    rack_group.append(displayio.TileGrid(rack_bmp, pixel_shader=palette4))

    # 2. Horizontal divider rule (228x2 at x=61, y=71)
    divider_bmp = displayio.Bitmap(ENERGY_BAR_WIDTH, 2, 4)
    for y in range(2):
        for x in range(ENERGY_BAR_WIDTH):
            divider_bmp[x, y] = 2
    divider_grid = displayio.TileGrid(
        divider_bmp, pixel_shader=palette4, x=TELEMETRY_TEXT_X, y=71
    )

    # 3. Dynamic segmented energy bar (228x10 at x=61, y=102)
    bar_bmp = displayio.Bitmap(ENERGY_BAR_WIDTH, ENERGY_BAR_HEIGHT, 4)
    for x in range(ENERGY_BAR_WIDTH):
        bar_bmp[x, 0] = 3
        bar_bmp[x, ENERGY_BAR_HEIGHT - 1] = 3
    for y in range(ENERGY_BAR_HEIGHT):
        bar_bmp[0, y] = 3
        bar_bmp[ENERGY_BAR_WIDTH - 1, y] = 3
    bar_grid = displayio.TileGrid(
        bar_bmp, pixel_shader=palette4, x=TELEMETRY_TEXT_X, y=102
    )

    group = displayio.Group()
    group.append(rack_group)
    group.append(divider_grid)
    group.append(bar_grid)
    return group, bar_bmp


def update_energy_bar(bar_bmp, energy_pct):
    """Fill the segmented energy bar proportionally to battery percentage (0-100)."""
    inner_width = ENERGY_BAR_WIDTH - 4
    filled = (inner_width * energy_pct) // 100
    for x in range(inner_width):
        color = 3 if (x < filled and (x % 8 != 7)) else 0
        for y in range(2, ENERGY_BAR_HEIGHT - 2):
            bar_bmp[x + 2, y] = color


def get_battery_percent():
    """Read MagTag LiPo voltage and map 3.30V-4.15V to 0-100%."""
    try:
        voltage = magtag.peripherals.battery
    except Exception:
        return 100
    if voltage < 2.5:
        return 100
    pct = int(round((voltage - 3.30) / (4.15 - 3.30) * 100))
    return max(0, min(100, pct))


root_group = get_root_group()

for x_pos, y_pos, anchor_x, anchor_y, scale, wrap in TEXT_LAYOUTS:
    magtag.add_text(
        text_wrap=wrap,
        text_maxlen=TEXT_MAXLEN,
        text_position=(x_pos, y_pos),
        line_spacing=LINE_SPACING,
        text_anchor_point=(anchor_x, anchor_y),
        text_scale=scale,
    )

# Pre-build all graphic overlay groups once
gcp_qr_group = build_qr_group(GCP_QR_SIZE, GCP_QR_BITS, scale=2, border=3, y_pos=8)
linkedin_qr_group = build_qr_group(LINKEDIN_QR_SIZE, LINKEDIN_QR_BITS, scale=3, border=2)
personal_vcard_qr_group = build_qr_group(
    PERSONAL_VCARD_QR_SIZE, PERSONAL_VCARD_QR_BITS, scale=2, border=3
)
telemetry_group, energy_bar_bmp = build_telemetry_group()

active_overlay_group = None
current_view = None
light_show_active = False
light_show_start = 0.0
telemetry_deadline = 0.0


def start_light_show():
    """Power on the 4 NeoPixels and start the Google 4-color wave."""
    global light_show_active, light_show_start
    pixels = magtag.peripherals.neopixels
    magtag.peripherals.neopixel_disable = False
    pixels.brightness = LIGHT_SHOW_BRIGHTNESS
    try:
        pixels.auto_write = False
    except AttributeError:
        pass
    light_show_start = time.monotonic()
    light_show_active = True
    update_light_show()


def update_light_show():
    """Smoothly cycle Google Blue, Red, Yellow, and Green across the 4 NeoPixels."""
    if not light_show_active:
        return
    pixels = magtag.peripherals.neopixels
    phase_base = (time.monotonic() - light_show_start) * LIGHT_SHOW_SPEED
    num_colors = len(GOOGLE_COLORS)

    for i in range(len(pixels)):
        pos = (phase_base + i) % num_colors
        idx0 = int(pos)
        idx1 = (idx0 + 1) % num_colors
        frac = pos - idx0
        c0 = GOOGLE_COLORS[idx0]
        c1 = GOOGLE_COLORS[idx1]
        pixels[i] = (
            int(c0[0] + (c1[0] - c0[0]) * frac),
            int(c0[1] + (c1[1] - c0[1]) * frac),
            int(c0[2] + (c1[2] - c0[2]) * frac),
        )
    try:
        pixels.show()
    except AttributeError:
        pass


def stop_light_show():
    """Turn off all NeoPixels and cut NeoPixel power to save battery."""
    global light_show_active
    if light_show_active:
        pixels = magtag.peripherals.neopixels
        pixels.fill((0, 0, 0))
        try:
            pixels.show()
        except AttributeError:
            pass
        magtag.peripherals.neopixel_disable = True
        light_show_active = False


def safe_refresh():
    """Wait until the e-ink display is ready and perform a guaranteed refresh."""
    for _ in range(30):
        while getattr(display, "busy", False):
            if light_show_active:
                update_light_show()
            time.sleep(0.05)
        wait = display.time_to_refresh
        if wait > 0:
            end_wait = time.monotonic() + wait + 0.1
            while time.monotonic() < end_wait:
                if light_show_active:
                    update_light_show()
                time.sleep(0.05)
        try:
            display.refresh()
            return
        except RuntimeError:
            time.sleep(0.25)


def wait_for_release(button_attr):
    """Wait until the pressed button is released and debounce switch bounce."""
    while getattr(magtag.peripherals, button_attr):
        if light_show_active:
            update_light_show()
        time.sleep(POLL_INTERVAL)
    time.sleep(DEBOUNCE_DELAY)


def clear_overlay():
    """Stop any active light show and remove any graphic overlay group."""
    global active_overlay_group
    stop_light_show()
    if active_overlay_group is not None:
        try:
            root_group.remove(active_overlay_group)
        except ValueError:
            pass
        active_overlay_group = None


def show_card(lines, slot_offset, view):
    """Display a 3-line text card and hide any active overlay."""
    global current_view
    clear_overlay()

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
    global active_overlay_group, current_view
    clear_overlay()

    for slot in range(len(TEXT_LAYOUTS)):
        if slot != QR_CAPTION_SLOT:
            magtag.set_text(" ", slot, False)
    magtag.set_text(caption if caption else " ", QR_CAPTION_SLOT, False)

    root_group.append(qr_group)
    active_overlay_group = qr_group

    safe_refresh()
    current_view = view


def show_telemetry():
    """Show the server rack + live battery telemetry and run the Google light show."""
    global active_overlay_group, current_view, telemetry_deadline
    clear_overlay()

    energy_pct = get_battery_percent()
    update_energy_bar(energy_bar_bmp, energy_pct)

    telemetry_lines = (
        "Thomas Leung",
        "HPC Troublemaker",
        f"NODE: login-001 | ENERGY: {energy_pct}% | READY",
    )
    active_slots = range(
        TELEMETRY_SLOT_OFFSET, TELEMETRY_SLOT_OFFSET + len(telemetry_lines)
    )
    for slot in range(len(TEXT_LAYOUTS)):
        if slot not in active_slots:
            magtag.set_text(" ", slot, False)

    for i, text in enumerate(telemetry_lines):
        magtag.set_text(text, TELEMETRY_SLOT_OFFSET + i, False)

    root_group.append(telemetry_group)
    active_overlay_group = telemetry_group

    # Start the Google color light show immediately while e-ink refreshes
    start_light_show()
    safe_refresh()
    telemetry_deadline = time.monotonic() + TELEMETRY_DURATION
    current_view = VIEW_TELEMETRY


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
        if current_view == VIEW_PERSONAL_CONTACT:
            show_qr(personal_vcard_qr_group, VIEW_PERSONAL_VCARD_QR)
        else:
            show_card(PERSONAL_CONTACT_LINES, CONTACT_SLOT_OFFSET, VIEW_PERSONAL_CONTACT)
        wait_for_release("button_c_pressed")

    elif magtag.peripherals.button_d_pressed:
        if current_view == VIEW_TELEMETRY:
            show_card(BADGE_LINES, BADGE_SLOT_OFFSET, VIEW_BADGE)
        else:
            show_telemetry()
        wait_for_release("button_d_pressed")

    elif current_view == VIEW_TELEMETRY:
        if time.monotonic() >= telemetry_deadline:
            show_card(BADGE_LINES, BADGE_SLOT_OFFSET, VIEW_BADGE)
        else:
            update_light_show()

    time.sleep(POLL_INTERVAL)
