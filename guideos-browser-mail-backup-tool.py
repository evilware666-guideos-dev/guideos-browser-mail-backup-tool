#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Browser & Mail Backup-Tool
================================
Sicherung & Wiederherstellung von Firefox, Chromium, Vivaldi,
LibreWolf, Chrome, Brave & Thunderbird – inklusive Snap/Flatpak.

Autor      : evilware666 & Helga
Version    : 1.4
Lizenz     : MIT
Plattform  : Linux (Debian/Ubuntu & Derivate)
GUI        : GTK4 + LibAdwaita
"""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib, Gio, Gdk
import os, glob, tarfile, shutil, subprocess, tempfile, threading, secrets, string, re
from datetime import datetime
from pathlib import Path

HOME = str(Path.home())

def find_first_existing(*patterns):
    for p in patterns:
        for c in sorted(glob.glob(p)):
            if os.path.isdir(c): return c
    return None

# Vollständige Pfade für alle Browser (alle Installationstypen)
PROFILE_PATHS = {
    "Firefox": (
        f"{HOME}/.mozilla/firefox",
        f"{HOME}/.mozilla",
        f"{HOME}/.config/mozilla/firefox",
        f"{HOME}/snap/firefox/*/common/.mozilla/firefox",
        f"{HOME}/snap/firefox/common/.mozilla/firefox",
        f"{HOME}/snap/firefox/current/common/.mozilla/firefox",
        f"{HOME}/snap/firefox/*/common/.mozilla",
        f"{HOME}/snap/firefox/common/.mozilla",
        f"{HOME}/snap/firefox/*/.mozilla/firefox",
        f"{HOME}/snap/firefox/*/.mozilla",
        f"{HOME}/.var/app/org.mozilla.firefox/.mozilla/firefox",
    ),
    "Chromium": (
        f"{HOME}/.config/chromium",
        f"{HOME}/snap/chromium/*/common/chromium",
        f"{HOME}/snap/chromium/common/chromium",
        f"{HOME}/snap/chromium/current/common/chromium",
        f"{HOME}/snap/chromium/*/common/.config/chromium",
        f"{HOME}/snap/chromium/common/.config/chromium",
        f"{HOME}/snap/chromium/current/common/.config/chromium",
        f"{HOME}/snap/chromium/*/.config/chromium",
        f"{HOME}/.var/app/org.chromium.Chromium/config/chromium",
        f"{HOME}/.var/app/org.chromium.Chromium/.config/chromium",
    ),
    "Vivaldi": (
        f"{HOME}/.config/vivaldi",
        f"{HOME}/snap/vivaldi/*/common/.config/vivaldi",
        f"{HOME}/snap/vivaldi/common/.config/vivaldi",
        f"{HOME}/snap/vivaldi/current/common/.config/vivaldi",
        f"{HOME}/snap/vivaldi/*/.config/vivaldi",
        f"{HOME}/.var/app/com.vivaldi.Vivaldi/config/vivaldi",
        f"{HOME}/.var/app/com.vivaldi.Vivaldi/.config/vivaldi",
    ),
    "LibreWolf": (
        f"{HOME}/.librewolf",
        f"{HOME}/.config/librewolf",
        f"{HOME}/snap/librewolf/*/common/.librewolf",
        f"{HOME}/snap/librewolf/common/.librewolf",
        f"{HOME}/snap/librewolf/current/common/.librewolf",
        f"{HOME}/snap/librewolf/*/.librewolf",
        f"{HOME}/.var/app/io.gitlab.librewolf-community/.librewolf",
    ),
    "Google Chrome": (
        f"{HOME}/.config/google-chrome",
        f"{HOME}/snap/google-chrome/*/common/.config/google-chrome",
        f"{HOME}/snap/google-chrome/common/.config/google-chrome",
        f"{HOME}/snap/google-chrome/current/common/.config/google-chrome",
        f"{HOME}/snap/google-chrome/*/.config/google-chrome",
        f"{HOME}/.var/app/com.google.Chrome/config/google-chrome",
        f"{HOME}/.var/app/com.google.Chrome/.config/google-chrome",
        f"{HOME}/.var/app/com.google.Chrome/config/google-chrome/Default",
        f"{HOME}/.var/app/com.google.Chrome/.config/google-chrome/Default",
    ),
    "Brave": (
        f"{HOME}/.config/BraveSoftware/Brave-Browser",
        f"{HOME}/.config/BraveSoftware",
        f"{HOME}/snap/brave/*/common/.config/BraveSoftware",
        f"{HOME}/snap/brave/common/.config/BraveSoftware",
        f"{HOME}/snap/brave/current/common/.config/BraveSoftware",
        f"{HOME}/snap/brave/*/common/.config/brave",
        f"{HOME}/snap/brave/*/.config/BraveSoftware",
        f"{HOME}/.var/app/com.brave.Browser/config/BraveSoftware/Brave-Browser",
        f"{HOME}/.var/app/com.brave.Browser/config/BraveSoftware",
        f"{HOME}/.var/app/com.brave.Browser/.config/BraveSoftware/Brave-Browser",
        f"{HOME}/.var/app/com.brave.Browser/.config/BraveSoftware",
        f"{HOME}/.var/app/com.brave.Browser/data/BraveSoftware",
    ),
    "Thunderbird": (
        f"{HOME}/.thunderbird",
        f"{HOME}/.config/thunderbird",
        f"{HOME}/snap/thunderbird/*/common/.thunderbird",
        f"{HOME}/snap/thunderbird/common/.thunderbird",
        f"{HOME}/snap/thunderbird/current/common/.thunderbird",
        f"{HOME}/snap/thunderbird/*/.thunderbird",
        f"{HOME}/.var/app/org.mozilla.Thunderbird/.thunderbird",
    ),
    "Geary": (
        f"{HOME}/.config/geary",
        f"{HOME}/.local/share/geary",
        f"{HOME}/snap/geary/*/common/.config/geary",
        f"{HOME}/snap/geary/common/.config/geary",
        f"{HOME}/snap/geary/current/common/.config/geary",
        f"{HOME}/snap/geary/*/common/.local/share/geary",
        f"{HOME}/snap/geary/common/.local/share/geary",
        f"{HOME}/snap/geary/*/.config/geary",
        f"{HOME}/snap/geary/*/.local/share/geary",
        f"{HOME}/.var/app/org.gnome.Geary/data/geary",
        f"{HOME}/.var/app/org.gnome.Geary",
        f"{HOME}/.var/app/org.gnome.Geary/.local/share/geary",
        f"{HOME}/.var/app/org.gnome.Geary/config/geary",
        f"{HOME}/.var/app/org.gnome.Geary/.config/geary",
    ),
}

def find_profile_path(profile):
    """Gibt den tatsächlich existierenden Profilordner zurück."""
    for pat in PROFILE_PATHS[profile]:
        for c in sorted(glob.glob(pat)):
            if not os.path.isdir(c):
                continue

            # Für Snap-Installationen
            if "/snap/" in c:
                # Chromium-basierte Browser (Chromium, Vivaldi, Brave, Chrome)
                if profile in ["Chromium", "Vivaldi", "Google Chrome", "Brave"]:
                    # Wichtig: Snap Chromium hat sein Profil in ~/snap/chromium/common/chromium/
                    common_dir = os.path.join(os.path.dirname(c), "common", profile.lower())
                    if os.path.isdir(common_dir):
                        if os.path.exists(os.path.join(common_dir, "Local State")):
                            return common_dir
                        if os.path.exists(os.path.join(common_dir, "Default")):
                            return common_dir
                        if len(os.listdir(common_dir)) > 0:
                            return common_dir
                    
                    # Auch in anderen common/ Unterordnern suchen
                    for root, dirs, files in os.walk(c):
                        if "Local State" in files or "Default" in dirs:
                            return root

                # Für Firefox/Thunderbird/LibreWolf
                elif profile in ["Firefox", "Thunderbird", "LibreWolf"]:
                    for root, dirs, files in os.walk(c):
                        if "profiles.ini" in files or "places.sqlite" in files:
                            return root

                # Für Geary
                elif profile == "Geary":
                    for root, dirs, files in os.walk(c):
                        if "geary.db" in files or "geary.ini" in files:
                            return root

                # Fallback: tiefsten nicht-leeren Ordner zurückgeben
                deepest = None
                for root, dirs, files in os.walk(c):
                    if dirs or files:
                        deepest = root
                if deepest:
                    return deepest

                continue

            # Native und Flatpak-Installationen
            if profile in ["Firefox", "Thunderbird", "LibreWolf"]:
                if os.path.exists(os.path.join(c, "profiles.ini")):
                    return c
                if os.path.exists(os.path.join(c, "places.sqlite")):
                    return c

            elif profile == "Geary":
                if os.path.exists(os.path.join(c, "geary.db")):
                    return c
                if os.path.exists(os.path.join(c, "geary.ini")):
                    return c
                if os.path.exists(os.path.join(c, "accounts")):
                    return c
                if c == f"{HOME}/.var/app/org.gnome.Geary":
                    if os.path.exists(os.path.join(c, "data", "geary", "geary.db")):
                        return os.path.join(c, "data", "geary")
                    if os.path.exists(os.path.join(c, "data", "geary")):
                        return os.path.join(c, "data", "geary")
                if len(os.listdir(c)) > 0:
                    return c

            elif profile == "Google Chrome":
                if os.path.exists(os.path.join(c, "Local State")):
                    return c
                if os.path.exists(os.path.join(c, "Default")):
                    if os.path.exists(os.path.join(c, "Default", "Cookies")):
                        return c
                    return c
                if os.path.exists(os.path.join(c, "First Run")):
                    return c
                for sub in os.listdir(c):
                    sub_path = os.path.join(c, sub)
                    if os.path.isdir(sub_path) and sub == "Default":
                        if os.path.exists(os.path.join(sub_path, "Cookies")):
                            return c
                        return c

            else:
                if os.path.exists(os.path.join(c, "Local State")):
                    return c
                if os.path.exists(os.path.join(c, "Default")):
                    return c
                for sub in os.listdir(c):
                    sub_path = os.path.join(c, sub)
                    if os.path.isdir(sub_path) and sub in ["Default", "Profile 1", "Profile 2"]:
                        return c
                if len(os.listdir(c)) > 0:
                    return c

    return None

def _best_restore_target(profile):
    """Ermittelt den besten Zielpfad für eine Wiederherstellung."""
    c = find_profile_path(profile)
    if c:
        return os.path.dirname(c), os.path.basename(c)

    for pat in PROFILE_PATHS[profile]:
        base = pat.split("*")[0].rstrip("/")
        parent = os.path.dirname(base)
        if os.path.isdir(parent):
            return parent, os.path.basename(base)

    d = PROFILE_PATHS[profile][0]
    return os.path.dirname(d), os.path.basename(d)

# Bekannte Binär-Namen je Browser (Debian-Paket, Snap, Flatpak)
BROWSER_BINARIES = {
    "Firefox":       ["firefox", "firefox-esr"],
    "Chromium":      ["chromium", "chromium-browser"],
    "Vivaldi":       ["vivaldi", "vivaldi-stable"],
    "LibreWolf":     ["librewolf"],
    "Google Chrome": ["google-chrome", "google-chrome-stable"],
    "Brave":         ["brave-browser", "brave"],
    "Thunderbird":   ["thunderbird"],
    "Geary":         ["geary"],
}

# Snap-Paket-Namen (vollständig)
SNAP_NAMES = {
    "Firefox":       "firefox",
    "Chromium":      "chromium",
    "Vivaldi":       "vivaldi",
    "LibreWolf":     "librewolf",
    "Google Chrome": "google-chrome",
    "Brave":         "brave",
    "Thunderbird":   "thunderbird",
    "Geary":         "geary",
}

# Flatpak IDs (vollständig)
FLATPAK_IDS = {
    "Firefox":       "org.mozilla.firefox",
    "Chromium":      "org.chromium.Chromium",
    "Vivaldi":       "com.vivaldi.Vivaldi",
    "LibreWolf":     "io.gitlab.librewolf-community",
    "Google Chrome": "com.google.Chrome",
    "Brave":         "com.brave.Browser",
    "Thunderbird":   "org.mozilla.Thunderbird",
    "Geary":         "org.gnome.Geary",
}

class InstallCache:
    """Cache für Snap/Flatpak-Ergebnisse um wiederholte subprocess-Aufrufe zu vermeiden"""
    _instance = None
    _snap_list = None
    _flatpak_list = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_snap_list(self):
        if self._snap_list is None:
            try:
                result = subprocess.run(["snap", "list"], capture_output=True, text=True, timeout=5)
                self._snap_list = result.stdout if result.returncode == 0 else ""
            except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
                self._snap_list = ""
        return self._snap_list

    def get_flatpak_list(self):
        if self._flatpak_list is None:
            try:
                result = subprocess.run(["flatpak", "list"], capture_output=True, text=True, timeout=5)
                self._flatpak_list = result.stdout if result.returncode == 0 else ""
            except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
                self._flatpak_list = ""
        return self._flatpak_list

def detect_profile(profile):
    """Prüft ob der Browser/Mail-Client installiert ist."""
    cache = InstallCache()

    binary_gefunden = any(shutil.which(b) for b in BROWSER_BINARIES.get(profile, []))

    snap_gefunden = False
    snap_list = cache.get_snap_list()
    if snap_list and profile in SNAP_NAMES:
        snap_gefunden = SNAP_NAMES[profile] in snap_list

    flatpak_gefunden = False
    flatpak_list = cache.get_flatpak_list()
    if flatpak_list and profile in FLATPAK_IDS:
        flatpak_gefunden = FLATPAK_IDS[profile] in flatpak_list

    installiert = binary_gefunden or snap_gefunden or flatpak_gefunden

    if installiert:
        return True, "Installiert"
    else:
        return False, "Nicht installiert"

def generate_password():
    alpha = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?"
    return ''.join(secrets.choice(alpha) for _ in range(20))

def check_password_strength(password):
    """Prüft Passwortstärke und gibt (Score, Nachricht, Farbe) zurück"""
    score = 0
    messages = []

    if len(password) >= 12:
        score += 1
    elif len(password) >= 8:
        pass
    else:
        messages.append("• Mindestens 8 Zeichen")

    if re.search(r'[A-Z]', password):
        score += 1
    else:
        messages.append("• Großbuchstaben (A-Z)")

    if re.search(r'[a-z]', password):
        score += 1
    else:
        messages.append("• Kleinbuchstaben (a-z)")

    if re.search(r'\d', password):
        score += 1
    else:
        messages.append("• Zahlen (0-9)")

    if re.search(r'[!@#$%^&*()\-_=+\[\]{}|;:,.<>?]', password):
        score += 1
    else:
        messages.append("• Sonderzeichen (!@#$%^&* etc.)")

    if score <= 2:
        strength = "schwach"
        color = "#e01b24"
        advice = "\n\nDieses Passwort ist leicht zu knacken!"
    elif score <= 4:
        strength = "mittel"
        color = "#f5c211"
        advice = "\n\nFür sensible Daten wird ein stärkeres Passwort empfohlen."
    else:
        strength = "stark"
        color = "#2ec27e"
        advice = ""

    msg = f"Stärke: {strength}"
    if messages:
        msg += "\n\nVerbesserungsvorschläge:\n" + "\n".join(messages)
    msg += advice

    return score, msg, color

def gpg_decrypt_with_password(gpg_file, output_file, password):
    """Entschlüsselt eine GPG-Datei mit einem Passwort - OHNE Terminal-Fenster"""
    try:
        cmd = [
            "gpg", "--batch", "--yes", "--quiet",
            "--passphrase-fd", "0",
            "--output", output_file,
            "--decrypt", gpg_file
        ]
        
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        _, err = proc.communicate(input=password.encode())
        
        if proc.returncode != 0:
            return False, f"Entschlüsselung fehlgeschlagen: {err.decode()}"
        
        return True, ""
    except Exception as e:
        return False, str(e)

def do_backup_tar(profile, backup_dir):
    c = find_profile_path(profile)
    if not c:
        return False, (
            f"Das {profile}-Profil wurde nicht gefunden.\n\n"
            f" ⚠️ ⚠️Bitte stelle sicher, dass {profile} mindestens einmal gestartet wurde.⚠️ ⚠️"
        )
    name = os.path.join(
        backup_dir,
        f"{profile.replace(' ','_')}_backup_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.tar.gz"
    )
    try:
        with tarfile.open(name, "w:gz") as t:
            t.add(c, arcname=os.path.basename(c))
    except Exception as e:
        if os.path.exists(name): os.remove(name)
        return False, f"Fehler: {e}"
    return True, name

def do_restore_unpack(profile, archive, tmp_dir):
    try:
        with tarfile.open(archive, "r:gz") as t:
            members = t.getnames()
        if not members:
            return False, "Archiv ist leer."

        top = members[0].split("/")[0]

        td, tb = _best_restore_target(profile)

        existing = os.path.join(td, tb)
        if os.path.exists(existing):
            shutil.move(
                existing,
                f"{existing}_backup_before_restore_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )

        etmp = os.path.join(tmp_dir, "extracted")
        os.makedirs(etmp, exist_ok=True)

        with tarfile.open(archive, "r:gz") as t:
            for m in t.getmembers():
                if os.path.isabs(m.name) or ".." in m.name:
                    continue
                m.uid = os.getuid(); m.gid = os.getgid()
                m.uname = m.gname = ""
                t.extract(m, path=etmp, set_attrs=False)

        ef = os.path.join(etmp, top)
        if not os.path.isdir(ef):
            return False, f"Ordner '{top}' nicht gefunden."

        os.makedirs(td, exist_ok=True)
        shutil.move(ef, existing)

        u = os.environ.get("USER", "")
        if os.getuid() != 0 and u:
            try:
                subprocess.run(["chown", "-R", f"{u}:{u}", existing], capture_output=True)
            except:
                pass

        for dp, _, fns in os.walk(existing):
            try: os.chmod(dp, 0o750)
            except: pass
            for fn in fns:
                try: os.chmod(os.path.join(dp, fn), 0o640)
                except: pass

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    return True, "Wiederherstellung abgeschlossen!\n\nBitte starte den Browser neu."

BROWSERS = ["Firefox","Chromium","Vivaldi","LibreWolf","Google Chrome","Brave","Thunderbird","Geary"]
ICONS = {
    "Firefox":       "\U0001f98a",
    "Chromium":      "\U0001f310",
    "Vivaldi":       "\U0001f3bb",
    "LibreWolf":     "\U0001f43a",
    "Google Chrome": "\U0001f535",
    "Brave":         "\U0001f981",
    "Thunderbird":   "\u26a1",
    "Geary":         "\U0001f4e7",
}

class BrowserBackupApp(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="de.guideos.browser-backup",
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self._show_startup_warning()

    def _show_startup_warning(self):
        dlg = Adw.Dialog()
        dlg.set_title("Browser & Mail Backup")
        dlg.set_content_width(460)
        dlg.set_content_height(320)
        dlg.set_can_close(False)
        tv = Adw.ToolbarView(); dlg.set_child(tv)
        hb = Adw.HeaderBar()
        hb.set_show_end_title_buttons(False)
        hb.set_show_start_title_buttons(False)
        tv.add_top_bar(hb)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        box.set_margin_top(24); box.set_margin_bottom(24)
        box.set_margin_start(24); box.set_margin_end(24)
        tv.set_content(box)
        t = Gtk.Label(label="\u26a0\ufe0f  Wichtiger Hinweis")
        t.add_css_class("title-2"); t.set_halign(Gtk.Align.CENTER)
        box.append(t)
        b = Gtk.Label()
        b.set_markup(
            "Alle Browser und Mail-Programme müssen vorher\n"
            "<b>vollständig geschlossen</b> sein!\n\n"
            "Andernfalls können Dateien gesperrt sein und die\n"
            "Sicherung oder Wiederherstellung fehlschlagen."
        )
        b.set_halign(Gtk.Align.CENTER); b.set_wrap(True); box.append(b)
        bb = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        bb.set_halign(Gtk.Align.CENTER); bb.set_margin_top(8)
        qb = Gtk.Button(label="Beenden")
        qb.add_css_class("destructive-action"); qb.add_css_class("pill")
        qb.set_size_request(130, 40)
        qb.connect("clicked", lambda b: self._startup_response("quit", dlg))
        ob = Gtk.Button(label="OK, alle geschlossen – weiter")
        ob.add_css_class("suggested-action"); ob.add_css_class("pill")
        ob.set_size_request(220, 40)
        ob.connect("clicked", lambda b: self._startup_response("ok", dlg))
        bb.append(qb); bb.append(ob); box.append(bb)
        dlg.present(None)

    def _startup_response(self, r, dlg):
        dlg.close()
        if r == "ok":
            self.win.present()
        else:
            self.quit()


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Browser & Mail Backup-Tool")
        self.set_default_size(640, 980)
        self.set_resizable(True)
        self.selected_profile = "Firefox"
        self.use_encryption = False
        self._build_ui()
        self._detect_profiles_async()

    def _build_ui(self):
        tv = Adw.ToolbarView(); self.set_content(tv)
        hb = Adw.HeaderBar()
        qb = Gtk.Button(label="Beenden")
        qb.add_css_class("destructive-action")
        qb.connect("clicked", lambda b: self.close())
        hb.pack_start(qb); tv.add_top_bar(hb)
        sc = Gtk.ScrolledWindow()
        sc.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        tv.set_content(sc)
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        sc.set_child(outer)

        hbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        hbox.set_margin_top(24); hbox.set_margin_bottom(16)
        hbox.set_margin_start(24); hbox.set_margin_end(24)
        tl = Gtk.Label(label="\U0001f5c4\ufe0f  Browser & Mail Backup")
        tl.add_css_class("title-1"); tl.set_halign(Gtk.Align.CENTER)
        sl = Gtk.Label(label="Sichere und stelle deine Browser-Profile wieder her")
        sl.add_css_class("dim-label"); sl.set_halign(Gtk.Align.CENTER)
        hbox.append(tl); hbox.append(sl); outer.append(hbox)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        content.set_margin_top(16); content.set_margin_bottom(24)
        content.set_margin_start(24); content.set_margin_end(24)
        outer.append(content)

        content.append(self._slabel("Schritt 1 – Was möchtest du tun?"))
        content.append(self._build_action_chooser())
        content.append(self._slabel("Schritt 2 – Welches Programm?"))
        content.append(self._build_browser_grid())
        self.enc_lbl = self._slabel("Schritt 3 – Verschlüsselung (optional)")
        content.append(self.enc_lbl)
        self.enc_box = self._build_encryption_section()
        content.append(self.enc_box)
        self.start_lbl = self._slabel("Schritt 4 – Los geht's!")
        content.append(self.start_lbl)
        content.append(self._build_start_button())
        self.status_box = self._build_status_area()
        content.append(self.status_box)
        self._update_view()

    def _slabel(self, text):
        l = Gtk.Label(label=text)
        l.add_css_class("heading"); l.set_halign(Gtk.Align.START); l.set_margin_top(4)
        return l

    def _build_action_chooser(self):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.set_homogeneous(True)
        self.btn_backup = self._acard("\U0001f4be", "Sichern", "Backup erstellen", active=True)
        self.btn_restore = self._acard("\U0001f4c2", "Wiederherstellen", "Backup einspielen")
        self.btn_restore.set_group(self.btn_backup)
        self.btn_backup.connect("toggled", self._on_action_changed)
        box.append(self.btn_backup); box.append(self.btn_restore)
        return box

    def _acard(self, icon, title, subtitle, active=False):
        btn = Gtk.ToggleButton(); btn.set_active(active)
        vb = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        vb.set_margin_top(12); vb.set_margin_bottom(12)
        for t, c in [(icon, "title-2"), (title, "heading"), (subtitle, "dim-label")]:
            l = Gtk.Label(label=t); l.add_css_class(c); vb.append(l)
        btn.set_child(vb); btn.add_css_class("card")
        return btn

    def _build_browser_grid(self):
        flow = Gtk.FlowBox()
        flow.set_max_children_per_line(4); flow.set_min_children_per_line(2)
        flow.set_selection_mode(Gtk.SelectionMode.NONE); flow.set_homogeneous(True)
        flow.set_row_spacing(8); flow.set_column_spacing(8)
        self.browser_buttons = {}; self.browser_status_labels = {}; first = None
        for browser in BROWSERS:
            btn = Gtk.ToggleButton()
            if first is None:
                first = btn; btn.set_active(True)
            else:
                btn.set_group(first)
            vb = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            vb.set_margin_top(10); vb.set_margin_bottom(8)
            vb.set_margin_start(6); vb.set_margin_end(6)
            il = Gtk.Label(label=ICONS.get(browser, "\U0001f310"))
            il.add_css_class("title-3")
            nl = Gtk.Label(label=browser)
            nl.set_wrap(True); nl.set_justify(Gtk.Justification.CENTER)
            vb.append(il); vb.append(nl)
            sr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
            sr.set_halign(Gtk.Align.CENTER)
            dot = Gtk.Label()
            dot.set_markup("<span foreground='#77767b'>●</span>")
            dot.set_valign(Gtk.Align.CENTER)
            stl = Gtk.Label(label="⏳ Prüfe...")
            stl.add_css_class("caption"); stl.add_css_class("dim-label")
            stl.set_valign(Gtk.Align.CENTER)
            sr.append(dot); sr.append(stl); vb.append(sr)
            btn.set_child(vb); btn.add_css_class("card")
            btn.connect("toggled", self._on_browser_selected, browser)
            self.browser_buttons[browser] = btn
            self.browser_status_labels[browser] = (dot, stl)
            w = Gtk.FlowBoxChild(); w.set_child(btn); w.set_focusable(False)
            flow.append(w)
        return flow

    def _build_encryption_section(self):
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        enc_row = Adw.ActionRow()
        enc_row.set_title("Backup verschlüsseln")
        enc_row.set_subtitle("Schützt das Backup mit GnuPG AES-256")
        self.enc_switch = Gtk.Switch(); self.enc_switch.set_valign(Gtk.Align.CENTER)
        self.enc_switch.connect("state-set", self._on_enc_toggled)
        enc_row.add_suffix(self.enc_switch)
        enc_row.set_activatable_widget(self.enc_switch)
        el = Gtk.ListBox()
        el.set_selection_mode(Gtk.SelectionMode.NONE); el.add_css_class("boxed-list")
        el.append(enc_row); outer.append(el)
        self.pw_box = self._build_pw_box()
        self.pw_box.set_visible(False)
        outer.append(self.pw_box)
        return outer

    def _build_pw_box(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        t = Gtk.Label(label="\U0001f511  Passwort für die Verschlüsselung")
        t.add_css_class("heading"); t.set_halign(Gtk.Align.START)
        box.append(t)

        h = Gtk.Label(label="Gib ein eigenes Passwort ein oder lass dir eines generieren.")
        h.add_css_class("dim-label"); h.set_halign(Gtk.Align.START); h.set_wrap(True)
        box.append(h)

        row1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        entry_box1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        entry_container1 = Gtk.ListBox()
        entry_container1.set_selection_mode(Gtk.SelectionMode.NONE)
        entry_container1.add_css_class("boxed-list"); entry_container1.set_hexpand(True)
        self.pw_entry = Gtk.Entry()
        self.pw_entry.set_placeholder_text("Passwort")
        self.pw_entry.set_visibility(False)
        self.pw_entry.connect("changed", self._on_password_changed)
        entry_container1.append(self.pw_entry)
        entry_box1.append(entry_container1)
        self.show_pw1_btn = Gtk.ToggleButton()
        self.show_pw1_btn.set_icon_name("eye-not-looking-symbolic")
        self.show_pw1_btn.set_valign(Gtk.Align.CENTER)
        self.show_pw1_btn.set_tooltip_text("Passwort anzeigen")
        self.show_pw1_btn.connect("toggled", self._on_toggle_password_visibility, self.pw_entry)
        entry_box1.append(self.show_pw1_btn)
        row1.append(entry_box1)
        self.strength_indicator = Gtk.Label(label="")
        self.strength_indicator.add_css_class("caption")
        self.strength_indicator.set_halign(Gtk.Align.START)
        self.strength_indicator.set_margin_start(12)
        row1.append(self.strength_indicator)
        box.append(row1)

        row2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        entry_container2 = Gtk.ListBox()
        entry_container2.set_selection_mode(Gtk.SelectionMode.NONE)
        entry_container2.add_css_class("boxed-list"); entry_container2.set_hexpand(True)
        self.pw_confirm_entry = Gtk.Entry()
        self.pw_confirm_entry.set_placeholder_text("Passwort wiederholen")
        self.pw_confirm_entry.set_visibility(False)
        self.pw_confirm_entry.connect("changed", self._on_password_changed)
        entry_container2.append(self.pw_confirm_entry)
        row2.append(entry_container2)
        self.show_pw2_btn = Gtk.ToggleButton()
        self.show_pw2_btn.set_icon_name("eye-not-looking-symbolic")
        self.show_pw2_btn.set_valign(Gtk.Align.CENTER)
        self.show_pw2_btn.set_tooltip_text("Passwort anzeigen")
        self.show_pw2_btn.connect("toggled", self._on_toggle_password_visibility, self.pw_confirm_entry)
        row2.append(self.show_pw2_btn)
        box.append(row2)

        self.confirm_status = Gtk.Label(label="")
        self.confirm_status.add_css_class("caption")
        self.confirm_status.set_halign(Gtk.Align.START)
        self.confirm_status.set_margin_start(12)
        box.append(self.confirm_status)

        bc = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        bc.set_halign(Gtk.Align.START)
        gb = Gtk.Button(label="\U0001f504  Generieren")
        gb.add_css_class("pill")
        gb.set_tooltip_text("Sicheres zufälliges Passwort erstellen")
        gb.connect("clicked", self._on_generate_pw)
        bc.append(gb)
        cb = Gtk.Button(label="\U0001f4cb  Kopieren")
        cb.add_css_class("pill")
        cb.set_tooltip_text("Passwort in Zwischenablage kopieren")
        cb.connect("clicked", self._on_copy_pw)
        bc.append(cb)
        box.append(bc)

        wl = Gtk.ListBox()
        wl.set_selection_mode(Gtk.SelectionMode.NONE); wl.add_css_class("boxed-list")
        wr = Adw.ActionRow()
        wr.set_title("\u26a0\ufe0f  Passwort sicher aufbewahren!")
        wr.set_subtitle(
            "Ohne dieses Passwort kann das Backup NICHT wiederhergestellt werden. "
            "Bitte in einem Passwort-Manager oder an einem sicheren Ort speichern."
        )
        wl.append(wr); box.append(wl)
        return box

    def _on_password_changed(self, entry):
        pw1 = self.pw_entry.get_text().strip()
        pw2 = self.pw_confirm_entry.get_text().strip()
        if pw1:
            score, msg, color = check_password_strength(pw1)
            self.strength_indicator.set_markup(f"<span foreground='{color}'>🔐 {msg}</span>")
            self.strength_indicator.set_visible(True)
        else:
            self.strength_indicator.set_visible(False)
        if pw1 and pw2:
            if pw1 == pw2:
                self.confirm_status.set_markup("<span foreground='#2ec27e'>✓ Passwörter stimmen überein</span>")
            else:
                self.confirm_status.set_markup("<span foreground='#e01b24'>✗ Passwörter stimmen nicht überein</span>")
        elif pw2:
            self.confirm_status.set_markup("<span foreground='#f5c211'>⚠ Bitte Passwort wiederholen</span>")
        else:
            self.confirm_status.set_label("")

    def _on_toggle_password_visibility(self, button, entry):
        if button.get_active():
            entry.set_visibility(True)
            button.set_icon_name("eye-symbolic")
        else:
            entry.set_visibility(False)
            button.set_icon_name("eye-not-looking-symbolic")

    def _build_start_button(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.start_btn = Gtk.Button(label="\U0001f4be  Sichern starten")
        self.start_btn.add_css_class("suggested-action"); self.start_btn.add_css_class("pill")
        self.start_btn.set_halign(Gtk.Align.CENTER); self.start_btn.set_size_request(280, 48)
        self.start_btn.connect("clicked", self._on_start_clicked)
        box.append(self.start_btn)
        return box

    def _build_status_area(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_visible(False)
        self.spinner = Gtk.Spinner(); self.spinner.set_size_request(32, 32)
        self.spinner.set_halign(Gtk.Align.CENTER)
        self.status_label = Gtk.Label(label="")
        self.status_label.set_wrap(True)
        self.status_label.set_justify(Gtk.Justification.CENTER)
        self.status_label.set_halign(Gtk.Align.CENTER)
        box.append(self.spinner); box.append(self.status_label)
        return box

    def _detect_profiles_async(self):
        def w():
            r = {b: detect_profile(b) for b in BROWSERS}
            GLib.idle_add(self._apply_profiles, r)
        threading.Thread(target=w, daemon=True).start()

    def _apply_profiles(self, results):
        for br, (found, info) in results.items():
            if br not in self.browser_status_labels: continue
            dot, stl = self.browser_status_labels[br]
            btn = self.browser_buttons[br]
            if found:
                dot.set_markup("<span foreground='#2ec27e' size='large'>✔</span>")
                stl.set_markup("<span foreground='#2ec27e'>Installiert</span>")
                stl.remove_css_class("dim-label")
                btn.set_tooltip_text("✅ Installiert")
            else:
                dot.set_markup("<span foreground='#e01b24' size='large'>✘</span>")
                stl.set_label("Nicht installiert")
                stl.add_css_class("dim-label")
                btn.set_tooltip_text("❌ Nicht installiert (Backup kann trotzdem wiederhergestellt werden)")
        return False

    def _on_action_changed(self, btn): self._update_view()

    def _on_browser_selected(self, btn, br):
        if btn.get_active(): self.selected_profile = br

    def _on_enc_toggled(self, sw, state):
        self.use_encryption = state; self.pw_box.set_visible(state); return False

    def _on_generate_pw(self, btn):
        pw = generate_password()
        self.pw_entry.set_text(pw)
        self.pw_confirm_entry.set_text(pw)
        Gdk.Display.get_default().get_clipboard().set(pw)
        self._info_dialog(
            "\U0001f4cb  Passwort generiert",
            f"Das Passwort wurde generiert und\nin die Zwischenablage kopiert:\n\n{pw}\n\n\u26a0\ufe0f Bitte jetzt sicher aufbewahren!"
        )

    def _on_copy_pw(self, btn):
        pw = self.pw_entry.get_text().strip()
        if not pw:
            self._show_error("Kein Passwort vorhanden.\nBitte zuerst eingeben oder generieren.")
            return
        Gdk.Display.get_default().get_clipboard().set(pw)
        self._info_dialog("\U0001f4cb  Kopiert", "Passwort wurde in die\nZwischenablage kopiert.")

    def _info_dialog(self, heading, body):
        dlg = Adw.AlertDialog(heading=heading, body=body)
        dlg.add_response("ok", "OK")
        dlg.present(self)

    def _check_password_and_continue(self, backup_dir):
        pw = self.pw_entry.get_text().strip()
        score, msg, color = check_password_strength(pw)
        if score >= 5:
            self._proceed_with_backup(backup_dir, pw)
            return
        dlg = Adw.AlertDialog()
        dlg.set_heading("⚠️ Schwaches Passwort erkannt")
        dlg.set_body(
            f"{msg}\n\nMöchtest du dieses Passwort trotzdem verwenden?\n\n"
            "Bei 'Nein' kannst du ein neues Passwort eingeben oder generieren."
        )
        dlg.add_response("cancel", "Nein, zurück zur Eingabe")
        dlg.add_response("continue", "Ja, trotzdem verwenden")
        dlg.set_response_appearance("continue", Adw.ResponseAppearance.DESTRUCTIVE)
        dlg.set_default_response("cancel")
        dlg.connect("response", self._on_weak_password_response, backup_dir, pw)
        dlg.present(self)

    def _on_weak_password_response(self, dialog, response, backup_dir, pw):
        dialog.close()
        if response == "continue":
            self._proceed_with_backup(backup_dir, pw)

    def _proceed_with_backup(self, backup_dir, pw):
        self._set_busy(True)
        def tw():
            ok, res = do_backup_tar(self.selected_profile, backup_dir)
            if not ok:
                GLib.idle_add(self._after_tar, ok, res, pw)
                return
            # Verschlüsselung mit gpg
            gpg_file = res + ".gpg"
            try:
                cmd = [
                    "gpg", "--batch", "--yes", "--quiet",
                    "--symmetric", "--cipher-algo", "AES256",
                    "--passphrase-fd", "0",
                    "--output", gpg_file, res
                ]
                proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                _, err = proc.communicate(input=pw.encode())
                ok_gpg = proc.returncode == 0
            except Exception as e:
                ok_gpg = False
                err = str(e).encode()
            os.remove(res)
            if ok_gpg:
                GLib.idle_add(self._after_tar, True, gpg_file, pw)
            else:
                GLib.idle_add(self._after_tar, False, f"Verschlüsselung fehlgeschlagen: {err.decode() if isinstance(err, bytes) else err}", pw)
        threading.Thread(target=tw, daemon=True).start()

    def _update_view(self):
        ib = self.btn_backup.get_active()
        self.enc_lbl.set_visible(ib); self.enc_box.set_visible(ib)
        if ib:
            self.start_lbl.set_label("Schritt 4 – Los geht's!")
            self.start_btn.set_label("\U0001f4be  Sichern starten")
        else:
            self.start_lbl.set_label("Schritt 3 – Los geht's!")
            self.start_btn.set_label("\U0001f4c2  Backup-Datei auswählen …")

    def _on_start_clicked(self, btn):
        if self.btn_backup.get_active():
            self._start_backup()
        else:
            self._show_restore_warning()

    def _start_backup(self):
        if self.use_encryption:
            pw = self.pw_entry.get_text().strip()
            pw_confirm = self.pw_confirm_entry.get_text().strip()
            if not pw:
                self._show_error("Bitte zuerst ein Passwort eingeben\noder auf \"\U0001f504 Generieren\" klicken.")
                return
            if pw != pw_confirm:
                self._show_error("Die eingegebenen Passwörter stimmen nicht überein.\nBitte wiederhole die Eingabe.")
                return
            if len(pw) < 6:
                self._show_error("Das Passwort muss mindestens 6 Zeichen lang sein.")
                return
        dlg = Gtk.FileDialog()
        dlg.set_title("Zielordner für das Backup auswählen")
        dlg.set_initial_folder(Gio.File.new_for_path(HOME))
        dlg.select_folder(self, None, self._on_backup_dir_chosen)

    def _on_backup_dir_chosen(self, dlg, result):
        try:
            backup_dir = dlg.select_folder_finish(result).get_path()
        except:
            return
        if self.use_encryption:
            self._check_password_and_continue(backup_dir)
        else:
            self._set_busy(True)
            def w():
                ok, res = do_backup_tar(self.selected_profile, backup_dir)
                return (True, f"Backup gespeichert:\n{res}") if ok else (False, res)
            self._run_thread(w)

    def _after_tar(self, ok, result, pw):
        self._set_busy(False)
        if ok:
            if result.endswith(".gpg"):
                self._show_success(
                    f"Backup verschlüsselt gespeichert:\n{result}\n\n"
                    "\u26a0\ufe0f Passwort sicher aufbewahren!\nOhne Passwort ist das Backup verloren."
                )
            else:
                self._show_success(f"Backup gespeichert:\n{result}")
        else:
            self._show_error(result)
        return False

    def _show_restore_warning(self):
        dlg = Adw.Dialog()
        dlg.set_title("\u26a0\ufe0f  Achtung")
        dlg.set_content_width(480); dlg.set_content_height(300)
        tv = Adw.ToolbarView(); dlg.set_child(tv)
        hb = Adw.HeaderBar()
        hb.set_show_end_title_buttons(False); hb.set_show_start_title_buttons(False)
        tv.add_top_bar(hb)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        box.set_margin_top(24); box.set_margin_bottom(24)
        box.set_margin_start(24); box.set_margin_end(24)
        tv.set_content(box)
        lbl = Gtk.Label()
        lbl.set_markup(
            "<span size='x-large' weight='bold'>\u26a0\ufe0f  ACHTUNG</span>\n\n"
            f"Das bestehende <b>{self.selected_profile}</b>-Profil wird\n"
            "<span foreground='#e01b24' weight='bold'>unwiderruflich überschrieben!</span>\n\n"
            "Stelle sicher, dass der Browser geschlossen ist.\n"
            "Bei .gpg-Backups wirst du nach dem Passwort gefragt."
        )
        lbl.set_halign(Gtk.Align.CENTER); lbl.set_wrap(True); box.append(lbl)
        bb = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        bb.set_halign(Gtk.Align.CENTER); bb.set_margin_top(8)
        cb = Gtk.Button(label="Abbrechen")
        cb.add_css_class("pill"); cb.set_size_request(130, 40)
        cb.connect("clicked", lambda b: dlg.close())
        ob = Gtk.Button(label="\u26a0\ufe0f  Ja, fortfahren")
        ob.add_css_class("destructive-action"); ob.add_css_class("pill"); ob.set_size_request(160, 40)
        ob.connect("clicked", lambda b: self._restore_confirmed(dlg))
        bb.append(cb); bb.append(ob); box.append(bb)
        dlg.present(self)

    def _restore_confirmed(self, dlg):
        dlg.close()
        fd = Gtk.FileDialog(); fd.set_title("Backup-Datei auswählen")
        filters = Gio.ListStore.new(Gtk.FileFilter)
        f1 = Gtk.FileFilter()
        f1.set_name("Backup-Dateien (*.tar.gz, *.gpg)")
        f1.add_pattern("*.tar.gz"); f1.add_pattern("*.gpg")
        f2 = Gtk.FileFilter(); f2.set_name("Alle Dateien"); f2.add_pattern("*")
        filters.append(f1); filters.append(f2); fd.set_filters(filters)
        fd.set_initial_folder(Gio.File.new_for_path(HOME))
        fd.open(self, None, self._on_backup_file_chosen)

    def _on_backup_file_chosen(self, dlg, result):
        try:
            bf = dlg.open_finish(result).get_path()
        except:
            return
        
        if bf.endswith(".gpg"):
            self._ask_for_password_and_restore(bf)
        else:
            tmp = tempfile.mkdtemp()
            self._run_thread(lambda: do_restore_unpack(self.selected_profile, bf, tmp))

    def _ask_for_password_and_restore(self, gpg_file):
        """Zeigt einen Passwort-Dialog für die Entschlüsselung an"""
        dlg = Adw.AlertDialog()
        dlg.set_heading("🔐 Passwort eingeben")
        dlg.set_body("Bitte gib das Passwort für die Entschlüsselung des Backups ein.")
        
        password_entry = Gtk.Entry()
        password_entry.set_placeholder_text("Passwort")
        password_entry.set_visibility(False)
        password_entry.set_hexpand(True)
        
        show_btn = Gtk.ToggleButton()
        show_btn.set_icon_name("eye-not-looking-symbolic")
        show_btn.set_tooltip_text("Passwort anzeigen")
        
        def toggle_visibility(btn):
            if btn.get_active():
                password_entry.set_visibility(True)
                btn.set_icon_name("eye-symbolic")
            else:
                password_entry.set_visibility(False)
                btn.set_icon_name("eye-not-looking-symbolic")
        
        show_btn.connect("toggled", toggle_visibility)
        
        entry_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        entry_box.append(password_entry)
        entry_box.append(show_btn)
        
        extra = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        extra.set_margin_top(8)
        extra.append(entry_box)
        
        dlg.set_extra_child(extra)
        dlg.add_response("cancel", "Abbrechen")
        dlg.add_response("ok", "Entschlüsseln")
        dlg.set_response_appearance("ok", Adw.ResponseAppearance.SUGGESTED)
        dlg.set_default_response("ok")
        
        dlg.connect("response", self._on_password_response, gpg_file, password_entry)
        dlg.present(self)

    def _on_password_response(self, dialog, response, gpg_file, password_entry):
        dialog.close()
        if response == "ok":
            password = password_entry.get_text().strip()
            if not password:
                self._show_error("Bitte ein Passwort eingeben.")
                return
            
            self._set_busy(True)
            tmp = tempfile.mkdtemp()
            decrypted = os.path.join(tmp, "decrypted.tar.gz")
            
            def w():
                ok, err = gpg_decrypt_with_password(gpg_file, decrypted, password)
                if not ok:
                    shutil.rmtree(tmp, ignore_errors=True)
                    GLib.idle_add(self._on_task_done, False, f"Entschlüsselung fehlgeschlagen:\n{err}")
                    return
                ok2, msg = do_restore_unpack(self.selected_profile, decrypted, tmp)
                GLib.idle_add(self._on_task_done, ok2, msg)
            
            threading.Thread(target=w, daemon=True).start()

    def _set_busy(self, busy):
        self.start_btn.set_sensitive(not busy)
        self.status_box.set_visible(busy)
        if busy:
            self.status_label.set_label("Bitte warten …")
            self.spinner.start()
        else:
            self.spinner.stop()

    def _run_thread(self, fn):
        self._set_busy(True)
        def w():
            ok, msg = fn()
            GLib.idle_add(self._on_task_done, ok, msg)
        threading.Thread(target=w, daemon=True).start()

    def _on_task_done(self, ok, msg):
        self._set_busy(False)
        if ok:
            self._show_success(msg)
        else:
            self._show_error(msg)
        return False

    def _show_success(self, msg):
        d = Adw.AlertDialog(heading="\u2705  Erfolgreich!", body=msg)
        d.add_response("ok", "OK")
        d.present(self)

    def _show_error(self, msg):
        d = Adw.AlertDialog(heading="\u274c  Fehler", body=msg)
        d.add_response("ok", "OK")
        d.set_response_appearance("ok", Adw.ResponseAppearance.DESTRUCTIVE)
        d.present(self)


if __name__ == "__main__":
    BrowserBackupApp().run()
