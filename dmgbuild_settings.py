# dmgbuild_settings.py
#
# Settings file for dmgbuild – creates a polished macOS DMG installer.
#
# ── USAGE ─────────────────────────────────────────────────────────────────────
#   pip install dmgbuild
#
#   dmgbuild -s dmgbuild_settings.py \
#             "Syllabus Copier-inator 1000" \
#             "dist/SyllabusCopierInator1000.dmg"
#
# Run this AFTER PyInstaller has produced:
#   dist/Syllabus Copier-inator 1000.app
# ─────────────────────────────────────────────────────────────────────────────

import os

# ── Paths ─────────────────────────────────────────────────────────────────────
APP_NAME    = "Syllabus Copier-inator 1000"
APP_BUNDLE  = f"dist/{APP_NAME}.app"
BACKGROUND  = None          # set to a path like "assets/dmg_background.png" if you have one
ICON        = "icon.icns"   if os.path.exists("icon.icns") else None

# ── DMG appearance ────────────────────────────────────────────────────────────
# Volume shown in Finder when DMG is mounted
application = APP_BUNDLE
appname     = APP_NAME

# Where icons sit in the DMG window (pixels from top-left)
icon_locations = {
    APP_NAME + ".app": (150, 180),
    "Applications":    (450, 180),
}

# Finder window size when DMG is opened
window_rect = ((200, 120), (620, 380))    # ((x, y), (width, height))

# ── Volume / filesystem settings ──────────────────────────────────────────────
format          = "UDBZ"        # bzip2-compressed – good balance of size vs speed
                                # Use "UDZO" for zlib, "ULFO" for lzfse (macOS 10.11+)
size            = None          # None = auto-size; or e.g. "200m" for 200 MB

filesystem      = "HFS+"        # standard macOS filesystem for DMGs
volume_name     = APP_NAME

# ── Visual options ────────────────────────────────────────────────────────────
background      = BACKGROUND    # None = default grey; point to a PNG for a custom look
icon_size       = 96            # icon size in pixels within the DMG window
text_size       = 13

# Show a shortcut to /Applications so users can drag-install
symlinks        = {"Applications": "/Applications"}

# Optional: set a custom volume icon (shown in Finder sidebar when mounted)
# volume_icon = "icon.icns"

# ── Files to include ──────────────────────────────────────────────────────────
files = [APP_BUNDLE]
