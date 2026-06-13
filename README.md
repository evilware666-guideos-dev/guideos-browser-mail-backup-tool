
# 📦 Browser & Mail Backup‑Tool v1.4 
### Sicherung & Wiederherstellung von Firefox, Chromium, Vivaldi, LibreWolf, Chrome, Brave Thunderbird & Geary
**Autor:** evilware666 & Helga   
**Version:** 1.4
**Plattform:** Linux (Debian/Ubuntu & Derivate)  
**GUI:** GTK4 + LibAdwaita  
**Lizenz:** MIT  

---

## 📝 Überblick

Das **Browser & Mail Backup‑Tool v3.2** ist ein modernes GTK4‑Programm zum **Sichern und Wiederherstellen** von Browser‑ und Mail‑Profilen.  
Es unterstützt sowohl klassische **Debian** Paketinstallationen als auch **Snap** und **Flatpak**.

Das Tool ist ideal für:

- Systemwechsel  
- Neuinstallationen  
- Umzüge zwischen Snap/Flatpak/Debian‑Paketen  
- Backups vor kritischen Updates  
- Vollautomatische Profil‑Migration  

Es bietet eine **intuitive Oberfläche**, automatische Profil‑Erkennung und optional eine **AES‑256‑Verschlüsselung** via GnuPG.

---

## ✨ Hauptfunktionen

### 🔍 Automatische Profil‑Erkennung
Das Tool erkennt Profile aus:

| Programm | Unterstützte Installationsarten |
|---------|--------------------------------|
| Firefox | Debian, Snap, Flatpak |
| Chromium | Debian, Snap, Flatpak |
| Vivaldi | Debian, Snap, Flatpak |
| LibreWolf | Debian, Snap, Flatpak |
| Google Chrome | Debian, Snap, Flatpak |
| Brave | Debian, Snap, Flatpak |
| Thunderbird | Debian, Snap, Flatpak |
| Geary | Debian, Snap, Flatpak |

Die Erkennung zeigt:
- Installationsart (Debian/Snap/Flatpak)
- Profilpfad
- Statusanzeige (grün = gefunden, grau = nicht installiert)

---

## 💾 Backup‑Funktionen

### 🔐 Optional: AES‑256‑Verschlüsselung
Das Tool kann Backups **vollständig verschlüsseln**:

- GnuPG AES‑256
- Passwortprüfung mit Stärke‑Analyse
- Passwort‑Generator (20 Zeichen, sicher)
- Passwort‑Wiederholung mit Übereinstimmungsprüfung
- Warnung bei schwachen Passwörtern
- Hinweis zur sicheren Aufbewahrung

### 📦 Backup‑Format
Backups werden erstellt als:

```
<Browser>_backup_YYYY-MM-DD_HH-MM-SS.tar.gz
(optional) .tar.gz.gpg bei Verschlüsselung
```

### 🔧 Backup‑Inhalt
Gesichert wird **das komplette Profilverzeichnis**, inklusive:

- Addons / Extensions  
- Verlauf  
- Cookies  
- Passwörter (sofern im Profil gespeichert)  
- Einstellungen  
- Mail‑Konten (Thunderbird)  
- Zertifikate  
- Session‑Daten  

---

## 🔁 Wiederherstellung

### ✔ Automatische Wiederherstellung
Das Tool:

1. Entpackt das Archiv  
2. Legt ein temporäres Arbeitsverzeichnis an  
3. Sichert vorhandene Profile als Backup  
4. Stellt das neue Profil wieder her  
5. Setzt Dateirechte korrekt  
6. Entfernt temporäre Dateien  

### 🔐 Bei verschlüsselten Backups
- GPG‑Dialog öffnet sich im Terminal  
- Passwort wird abgefragt  
- Archiv wird entschlüsselt und geprüft  

---

## 🖥 Benutzeroberfläche

### Startdialog
Beim Start erscheint ein Hinweis:

> „Alle Browser und Mail‑Programme müssen vollständig geschlossen sein!“

### Hauptfenster
Besteht aus:

- **Schritt 1:** Backup oder Wiederherstellung  
- **Schritt 2:** Browser/Mail‑Programm auswählen  
- **Schritt 3:** Verschlüsselung (optional)  
- **Schritt 4:** Backup starten oder Datei auswählen  
- **Statusbereich** mit Spinner & Meldungen  

---

## 🔐 Passwort‑Funktionen

### Passwort‑Stärkeanalyse
Bewertet anhand von:

- Länge  
- Großbuchstaben  
- Kleinbuchstaben  
- Zahlen  
- Sonderzeichen  

Farbcodierung:

| Stärke | Farbe |
|--------|--------|
| schwach | rot |
| mittel | gelb |
| stark | grün |

### Passwort‑Generator
Erstellt sichere Passwörter mit:

- 20 Zeichen  
- Groß/Klein  
- Zahlen  
- Sonderzeichen  

### Passwort‑Sichtbarkeit
Beide Felder haben einen „Auge“-Button.

---

## 🛠 Technische Details

### Technologien
- **GTK4**  
- **LibAdwaita**  
- **Python 3**  
- **GnuPG**  
- **tarfile**  
- **glob**  
- **Threading** für asynchrone Operationen  

### Sicherheit
- Keine Passwörter werden gespeichert  
- Passwort wird nur im RAM gehalten  
- GPG‑Verschlüsselung erfolgt lokal  
- Keine Internetverbindung notwendig  

---

## 📥 Installation

### Voraussetzungen
```
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1
sudo apt install gpg tar
```

### Starten
```
python3 browser_backup.py
```

---

## 📂 Backup‑Speicherort

Du kannst jeden Ordner wählen, z. B.:

- Externe Festplatte  
- USB‑Stick  
- NAS  
- Cloud‑Ordner (Nextcloud, Dropbox, etc.)  

---

## ⚠️ Wichtige Hinweise

- Browser **müssen geschlossen** sein  
- Verschlüsselte Backups sind **ohne Passwort verloren**  
- Snap/Flatpak‑Profile können andere Pfade haben  
- Große Profile (Thunderbird) können mehrere GB groß sein  

---

## 🧪 Getestete Systeme

- Debian 12  
- Ubuntu 22.04 / 24.04  
- Linux Mint 21  
- Pop!_OS  
- Zorin OS  
- MX Linux  

---

## 🧩 Bekannte Einschränkungen

- Kein Live‑Backup während Browser läuft  
- GPG‑Terminalfenster kann je nach Desktop variieren  
- Flatpak‑Sandbox kann manche Pfade verstecken  

