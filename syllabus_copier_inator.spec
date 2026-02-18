# syllabus_copier_inator.spec
#
# PyInstaller spec file for Syllabus Copier-inator 1000
#
# ── USAGE ─────────────────────────────────────────────────────────────────────
#
#  Windows (produces dist/SyllabusCopierInator1000.exe):
#    pyinstaller syllabus_copier_inator.spec
#
#  macOS – app bundle (produces dist/Syllabus Copier-inator 1000.app):
#    pyinstaller syllabus_copier_inator.spec
#
#  macOS – DMG  (run AFTER the .app has been built):
#    pip install dmgbuild
#    dmgbuild -s dmgbuild_settings.py "Syllabus Copier-inator 1000" \
#             "dist/SyllabusCopierInator1000.dmg"
#    (see the companion dmgbuild_settings.py file)
#
# ── REQUIREMENTS ──────────────────────────────────────────────────────────────
#   pip install pyinstaller            # all platforms
#   pip install dmgbuild               # macOS DMG only
#
# ── ICON NOTE ─────────────────────────────────────────────────────────────────
#   Place your icon files next to this spec before building:
#     icon.ico   – Windows  (256×256 multi-resolution ICO)
#     icon.icns  – macOS    (use iconutil or an online converter)
#   If you have neither, remove the icon= lines below and PyInstaller will
#   use its default icon.
# ─────────────────────────────────────────────────────────────────────────────

import sys
import os

block_cipher = None

APP_NAME        = "Syllabus Copier-inator 1000"
EXE_NAME        = "SyllabusCopierInator1000"   # no spaces – friendlier on Windows
SCRIPT          = "syllabus_copier_inator.py"
ICON_WIN        = "icon.ico"   if os.path.exists("icon.ico")  else None
ICON_MAC        = "icon.icns"  if os.path.exists("icon.icns") else None

IS_MAC          = sys.platform == "darwin"
IS_WIN          = sys.platform == "win32"

# ── Analysis ──────────────────────────────────────────────────────────────────
a = Analysis(
    [SCRIPT],
    pathex=[],
    binaries=[],
    datas=[
        # Add extra data files here as (src, dest_folder) tuples, e.g.:
        # ("assets/", "assets"),
    ],
    hiddenimports=[
        # tkinter sub-modules that are occasionally missed on some platforms
        "tkinter",
        "tkinter.ttk",
        "tkinter.filedialog",
        "tkinter.messagebox",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Trim the bundle by excluding heavy unused packages
        "matplotlib", "numpy", "pandas", "PIL", "scipy",
        "PyQt5", "PyQt6", "wx",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# ── PYZ archive ───────────────────────────────────────────────────────────────
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ── EXE (the actual executable / launcher) ────────────────────────────────────
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,          # binaries go into COLLECT, keeping exe small
    name=EXE_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                       # compress with UPX if available; set False to skip
    console=False,                  # False = no terminal window on launch (GUI app)
    disable_windowed_traceback=False,
    target_arch=None,               # None = native arch; set "x86_64" or "arm64" to cross-compile
    codesign_identity=None,         # macOS: set to your Developer ID string to sign
    entitlements_file=None,
    icon=ICON_WIN if IS_WIN else ICON_MAC,
)

# ── COLLECT (one-dir bundle, easier to inspect / debug) ──────────────────────
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=EXE_NAME,
)

# ── BUNDLE (.app) – macOS only ────────────────────────────────────────────────
if IS_MAC:
    app = BUNDLE(
        coll,
        name=f"{APP_NAME}.app",
        icon=ICON_MAC,
        bundle_identifier="edu.university.syllabus-copier-inator",
        version="1.0.0",
        info_plist={
            # Human-readable name shown in the Dock / Finder
            "CFBundleDisplayName": APP_NAME,
            "CFBundleName": APP_NAME,
            "CFBundleShortVersionString": "1.0.0",
            "CFBundleVersion": "1.0.0",
            # Allow opening from anywhere (bypasses some Gatekeeper prompts)
            "LSMinimumSystemVersion": "10.13.0",
            # Declare that this is a GUI app (no Dock icon suppression)
            "LSUIElement": False,
            # High-resolution display support
            "NSHighResolutionCapable": True,
            # Required on macOS 10.15+ to access user-selected files
            "NSDocumentsFolderUsageDescription":
                "Syllabus Copier-inator needs access to read and copy your syllabus PDFs.",
            "NSDesktopFolderUsageDescription":
                "Syllabus Copier-inator needs access to read and copy your syllabus PDFs.",
        },
    )
