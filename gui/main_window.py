import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit,
    QFileDialog, QProgressBar, QGroupBox, QRadioButton,
    QStackedWidget, QFrame, QDialog
)
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QPainterPath, QPen, QColor
from PyQt5.QtCore import Qt, QTimer
from gui.worker import CrackerWorker

class HackerPopup(QDialog):
    def __init__(self, title, message, status="success", parent=None):
        super().__init__(parent)
        self.setFixedSize(460, 230)
        self.setStyleSheet("background-color: #0A0A0A; border: 1px solid #333333;")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        if status == "success" or status is True:
            color = "#00FF41" # Neon Green
        elif status == "info":
            color = "#00E5FF" # Electric Cyan
        elif status == "warn":
            color = "#FFB800" # Warning Amber
        else:
            color = "#FF003C" # Error Red
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"color: {color}; font-size: 22px; font-family: Consolas; font-weight: bold; border: none;")
        lbl_title.setAlignment(Qt.AlignCenter)
        
        lbl_msg = QLabel(message)
        lbl_msg.setWordWrap(True)
        lbl_msg.setStyleSheet("color: #DDDDDD; font-size: 15px; font-family: Consolas; border: none;")
        lbl_msg.setAlignment(Qt.AlignCenter)
        
        btn_close = QPushButton("ACKNOWLEDGE")
        btn_close.setFixedWidth(180)
        btn_close.setStyleSheet(f"background-color: #121212; color: {color}; border: 1px solid {color}; padding: 8px; font-weight: bold; font-family: Segoe UI;")
        btn_close.clicked.connect(self.accept)
        
        layout.addWidget(lbl_title)
        layout.addSpacing(20)
        layout.addWidget(lbl_msg)
        layout.addSpacing(20)
        layout.addWidget(btn_close, alignment=Qt.AlignCenter)

class HackerMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KALOYA PDF CRACKER | By Haseeb Kaloya")
        self.resize(1000, 680)
        self.setMinimumSize(880, 600)
        
        # Dark Titlebar & Neon Text (Windows 11)
        import platform
        if platform.system() == "Windows":
            import ctypes
            try:
                DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                DWMWA_CAPTION_COLOR = 35
                DWMWA_TEXT_COLOR = 36
                set_window_attribute = ctypes.windll.dwmapi.DwmSetWindowAttribute
                get_parent = ctypes.windll.user32.GetParent
                hwnd = get_parent(int(self.winId())) if get_parent(int(self.winId())) else int(self.winId())
                
                # Immersive Dark Mode
                dark_val = ctypes.c_int(2)
                set_window_attribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(dark_val), ctypes.sizeof(dark_val))
                
                # Deep Dark Titlebar Background (#0A0A0A)
                caption_black = ctypes.c_int(0x000A0A0A)
                set_window_attribute(hwnd, DWMWA_CAPTION_COLOR, ctypes.byref(caption_black), ctypes.sizeof(caption_black))
                
                # Neon Green Title Text (COLORREF format: 0x00bbggrr -> 0x0041FF00)
                neon_green = ctypes.c_int(0x0041FF00)
                set_window_attribute(hwnd, DWMWA_TEXT_COLOR, ctypes.byref(neon_green), ctypes.sizeof(neon_green))
            except Exception:
                pass
        
        # Window Branding
        icon_path = os.path.join(os.path.dirname(__file__), "logo.ico")
        if os.path.isfile(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        self.worker = None

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Sidebar ──
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)

        # Branding Logo in Sidebar
        self.logo_label = QLabel()
        logo_pix = QPixmap(os.path.join(os.path.dirname(__file__), "logo.png"))
        if not logo_pix.isNull():
            self.logo_label.setPixmap(logo_pix.scaled(105, 105, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(self.logo_label)
        sidebar_layout.addSpacing(10)

        self.title_lbl = QLabel("")
        self.title_lbl.setObjectName("titleLabel")
        self.title_lbl.setAlignment(Qt.AlignCenter)
        self.title_lbl.setFixedHeight(84)
        
        self.final_title_html = (
            "<div align='center' style='line-height: 125%;'>"
            "<span style='font-family: \"Segoe UI\", Arial, sans-serif; font-size: 22px; font-weight: 900; color: #FFFFFF; letter-spacing: 2.5px;'>KALOYA</span><br>"
            "<span style='font-family: \"Segoe UI\", Arial, sans-serif; font-size: 14px; font-weight: 800; color: #00FF41; letter-spacing: 1.8px;'>PDF CRACKER</span><br>"
            "<span style='font-family: Consolas, monospace; font-size: 9px; font-weight: bold; color: #00FF41; letter-spacing: 0.8px;'>● PRO SUITE</span>"
            "</div>"
        )
        self.final_title = "KALOYA PDF CRACKER"
        self.current_title_len = 0
        self.title_timer = QTimer(self)
        self.title_timer.timeout.connect(self.animate_title)
        self.title_timer.start(40) # FAST cyber decoder effect
        
        sidebar_layout.addWidget(self.title_lbl)
        sidebar_layout.addSpacing(6)

        # Glowing Neon Divider
        brand_divider = QFrame()
        brand_divider.setObjectName("brandDivider")
        brand_divider.setFixedHeight(1)
        sidebar_layout.addWidget(brand_divider)
        sidebar_layout.addSpacing(20)

        btn_dash = QPushButton("DASHBOARD")
        btn_dash.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        btn_disclaimer = QPushButton("DISCLAIMER")
        btn_disclaimer.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        btn_about = QPushButton("ABOUT")
        btn_about.clicked.connect(lambda: self.stack.setCurrentIndex(2))

        sidebar_layout.addWidget(btn_dash)
        sidebar_layout.addSpacing(10)
        sidebar_layout.addWidget(btn_disclaimer)
        sidebar_layout.addSpacing(10)
        sidebar_layout.addWidget(btn_about)
        sidebar_layout.addStretch()

        # ── Developer Profile Card at Bottom of Sidebar ──
        dev_card = QFrame()
        dev_card.setObjectName("devCard")
        dev_card.setCursor(Qt.PointingHandCursor)
        dev_card.setToolTip("Click to view Developer Information")
        dev_card.mousePressEvent = lambda e: self.stack.setCurrentIndex(2)

        dev_card_layout = QVBoxLayout(dev_card)
        dev_card_layout.setContentsMargins(6, 8, 6, 8)
        dev_card_layout.setSpacing(4)
        dev_card_layout.setAlignment(Qt.AlignCenter)

        # Circular Avatar
        photo_path = os.path.join(os.path.dirname(__file__), "HaseebKaloya.jpg")
        avatar_label = QLabel()
        avatar_label.setAlignment(Qt.AlignCenter)
        if os.path.isfile(photo_path):
            avatar_pix = self.create_circular_avatar(photo_path, size=50)
            if not avatar_pix.isNull():
                avatar_label.setPixmap(avatar_pix)
        dev_card_layout.addWidget(avatar_label)

        # Developer Name
        lbl_dev_name = QLabel("Haseeb Kaloya")
        lbl_dev_name.setObjectName("devName")
        lbl_dev_name.setAlignment(Qt.AlignCenter)
        dev_card_layout.addWidget(lbl_dev_name)

        # Developer Role & Status
        lbl_dev_role = QLabel("● Lead Developer")
        lbl_dev_role.setObjectName("devRole")
        lbl_dev_role.setAlignment(Qt.AlignCenter)
        dev_card_layout.addWidget(lbl_dev_role)

        sidebar_layout.addWidget(dev_card)

        self.stack = QStackedWidget()
        self.stack.setContentsMargins(15, 15, 15, 15)

        self.page_dash = QWidget()
        dash_layout = QVBoxLayout(self.page_dash)
        dash_layout.setSpacing(15)

        # PDF Selection
        target_group = QGroupBox("TARGET SELECTION")
        target_layout = QHBoxLayout(target_group)
        self.txt_pdf = QLineEdit()
        self.txt_pdf.setPlaceholderText("Select Locked PDF...")
        self.txt_pdf.setReadOnly(True)
        btn_browse_pdf = QPushButton("BROWSE")
        btn_browse_pdf.setFixedWidth(80)
        btn_browse_pdf.clicked.connect(self.browse_pdf)
        target_layout.addWidget(self.txt_pdf)
        target_layout.addWidget(btn_browse_pdf)
        dash_layout.addWidget(target_group)

        # Attack Configuration
        attack_group = QGroupBox("ATTACK VECTOR")
        attack_layout = QVBoxLayout(attack_group)
        
        mode_layout = QHBoxLayout()
        self.radio_digits = QRadioButton("Dynamic Digits (Mask)")
        self.radio_digits.setChecked(True)
        self.radio_wordlist = QRadioButton("Dictionary Attack (File)")
        self.radio_wordlist.toggled.connect(self.toggle_modes)
        mode_layout.addWidget(self.radio_digits)
        mode_layout.addWidget(self.radio_wordlist)
        attack_layout.addLayout(mode_layout)

        # Payload Config Layout
        self.payload_layout = QHBoxLayout()
        
        # Digits Input
        self.lbl_digits = QLabel("Length:")
        self.txt_digits = QLineEdit()
        self.txt_digits.setPlaceholderText("e.g. 4-6 or 6")
        self.txt_digits.setText("4-6")
        self.payload_layout.addWidget(self.lbl_digits)
        self.payload_layout.addWidget(self.txt_digits)

        # Wordlist Input (Hidden by default)
        self.lbl_wordlist = QLabel("Dictionary:")
        self.lbl_wordlist.hide()
        self.txt_wordlist = QLineEdit()
        self.txt_wordlist.setPlaceholderText("Select wordlist.txt...")
        self.txt_wordlist.setReadOnly(True)
        self.txt_wordlist.hide()
        self.btn_wordlist = QPushButton("BROWSE")
        self.btn_wordlist.setFixedWidth(80)
        self.btn_wordlist.clicked.connect(self.browse_wordlist)
        self.btn_wordlist.hide()
        
        self.payload_layout.addWidget(self.lbl_wordlist)
        self.payload_layout.addWidget(self.txt_wordlist)
        self.payload_layout.addWidget(self.btn_wordlist)
        
        attack_layout.addLayout(self.payload_layout)
        dash_layout.addWidget(attack_group)

        # Console Header with Clear Button
        console_header = QHBoxLayout()
        console_lbl = QLabel("LIVE HACK TERMINAL:")
        console_lbl.setStyleSheet("color: #00FF41; font-weight: bold;")
        
        btn_clear = QPushButton("CLEAR TERMINAL")
        btn_clear.setFixedWidth(130)
        btn_clear.setStyleSheet("background-color: #121212; color: #888888; border: 1px solid #333333; padding: 4px; font-size: 11px;")

        console_header.addWidget(console_lbl)
        console_header.addStretch()
        console_header.addWidget(btn_clear)
        dash_layout.addLayout(console_header)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setText("[SYSTEM] Waiting for target...\n")
        btn_clear.clicked.connect(self.console.clear)
        dash_layout.addWidget(self.console)

        # Progress UI
        self.progress = QProgressBar()
        self.progress.setRange(0, 0) # indeterminate
        self.progress.hide()
        
        self.btn_attack = QPushButton("INITIATE CRACK")
        self.btn_attack.setStyleSheet("background-color: #330000; color: #FF003C; border: 1px solid #FF003C;")
        self.btn_attack.clicked.connect(self.start_or_abort_attack)

        dash_layout.addWidget(self.progress)
        dash_layout.addWidget(self.btn_attack)

        self.stack.addWidget(self.page_dash)


        # Page 1: Disclaimer
        self.page_disclaimer = QWidget()
        disclaimer_layout = QVBoxLayout(self.page_disclaimer)
        disclaimer_layout.setAlignment(Qt.AlignCenter)
        
        disc_text = (
            "<div style='text-align: center; margin-bottom: 20px;'>"
            "<span style='color: #FF003C; font-size: 26px; font-family: Consolas; font-weight: bold; letter-spacing: 2px;'>[RESTRICTED AREA] WARNING</span>"
            "</div><br>"
            "<p style='color: #DDDDDD; font-size: 15px; font-family: Segoe UI; line-height: 1.6;'>"
            "<b>Proceed with extreme caution.</b> You are accessing a highly optimized, weaponized cryptographic payload.<br><br>"
            "This software is designed to systematically breach AES/RC4 security protocols at hardware-level speeds. It is "
            "engineered <b>strictly</b> for white-hat cryptographic research and the recovery of compromised digital property that you legally own.<br><br>"
            "<span style='color: #FF003C;'><b>UNAUTHORIZED DEPLOYMENT ON EXTERNAL SERVERS, DATABASES, OR DOCUMENTS BELONGING TO THIRD PARTIES IS A FEDERAL OFFENSE.</b></span><br><br>"
            "By dragging digital assets into this environment and initiating the cracking engine, you acknowledge full liability. "
            "The architect of Kaloya PDF Cracker is completely immunized against any legal repercussions resulting from target mismanagement.<br><br>"
            "<b>USE THIS POWER RESPONSIBLY.</b>"
            "</p>"
        )
        lbl_disc_info = QLabel(disc_text)
        lbl_disc_info.setWordWrap(True)
        lbl_disc_info.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        disclaimer_layout.addWidget(lbl_disc_info)
        disclaimer_layout.addStretch()

        self.stack.addWidget(self.page_disclaimer)


        # Page 2: About
        self.page_about = QWidget()
        about_layout = QVBoxLayout(self.page_about)
        about_layout.setAlignment(Qt.AlignCenter)
        about_layout.setContentsMargins(40, 40, 40, 40)
        
        about_text = (
            "<div style='text-align: center; margin-bottom: 20px;'>"
            "<span style='color: #00FF41; font-size: 28px; font-family: Consolas; font-weight: bold; letter-spacing: 2px;'>KALOYA PDF CRACKER v1.0</span>"
            "</div>"
            "<p style='color: #DDDDDD; font-size: 15px; font-family: Segoe UI; line-height: 1.6;'>"
            "I engineered this tactical interface to bring raw, untamed decryption power directly to your screen. "
            "Kaloya PDF Cracker bypasses inefficient generic routines to deliver devastating brute-force speed, silently stripping encryptions in the background.<br><br>"
            "Powered locally by the legendary <b>John the Ripper</b> architecture, it slices through standard commercial encryption logic dynamically, leaving "
            "zero room for target survival. No external servers. No telemetry. Just raw processing dominance.<br><br>"
            "<span style='color: #00FF41; font-family: Consolas;'>[DEVELOPER] : Haseeb Kaloya</span><br>"
            "<span style='color: #00FF41; font-family: Consolas;'>[CONTACT]       : contact.haseebkaloya@gmail.com</span>"
            "</p>"
        )
        lbl_about_info = QLabel(about_text)
        lbl_about_info.setWordWrap(True)
        lbl_about_info.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Interactive Buttons Layout
        import webbrowser
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.btn_email = QPushButton("SECURE EMAIL")
        self.btn_email.setStyleSheet("background-color: #121212; color: #00FF41; border: 1px solid #00FF41;")
        
        def copy_email_to_clip():
            from PyQt5.QtWidgets import QApplication
            from PyQt5.QtCore import QTimer
            QApplication.clipboard().setText("contact.haseebkaloya@gmail.com")
            self.btn_email.setText("COPIED TO CLIPBOARD!")
            QTimer.singleShot(2000, lambda: self.btn_email.setText("SECURE EMAIL"))
            
        self.btn_email.clicked.connect(copy_email_to_clip)
        
        btn_github = QPushButton("GITHUB SOURCE")
        btn_github.setStyleSheet("background-color: #121212; color: #FFFFFF; border: 1px solid #555555;")
        btn_github.clicked.connect(lambda: webbrowser.open("https://github.com/HaseebKaloya"))

        btn_layout.addWidget(self.btn_email)
        btn_layout.addWidget(btn_github)
        
        about_layout.addWidget(lbl_about_info)
        about_layout.addSpacing(20)
        about_layout.addLayout(btn_layout)
        about_layout.addStretch()

        self.stack.addWidget(self.page_about)


        # Add to main
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stack, 1)

    def toggle_modes(self):
        is_wordlist = self.radio_wordlist.isChecked()
        self.lbl_digits.setVisible(not is_wordlist)
        self.txt_digits.setVisible(not is_wordlist)
        
        self.lbl_wordlist.setVisible(is_wordlist)
        self.txt_wordlist.setVisible(is_wordlist)
        self.btn_wordlist.setVisible(is_wordlist)

    def browse_pdf(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select Locked PDF", "", "PDF Files (*.pdf)")
        if f:
            self.txt_pdf.setText(f)
            import cracker
            status, _, detail = cracker.check_pdf_encryption(f)
            if status == "NOT_ENCRYPTED":
                self.log_console(f"\n[TARGET LOADED] {os.path.basename(f)}\n[NOTICE] This PDF is NOT password protected. It is already unlocked!\n")
            elif status == "ENCRYPTED":
                self.log_console(f"\n[TARGET LOADED] {os.path.basename(f)}\n[STATUS] Password Protected ({detail})\n")
            elif status == "UNSUPPORTED":
                self.log_console(f"\n[TARGET LOADED] {os.path.basename(f)}\n[WARN] Unsupported PDF security: {detail}\n")
            else:
                self.log_console(f"\n[TARGET LOADED] {os.path.basename(f)}\n")

    def browse_wordlist(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select Dictionary", "", "Text Files (*.txt)")
        if f:
            self.txt_wordlist.setText(f)

    def log_console(self, text):
        import re
        # Strip ANSI terminal colors/formatting so it renders cleanly
        clean_text = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', text)
        clean_text = clean_text.replace('\r', '')
        if clean_text.strip():
            self.console.insertPlainText(clean_text)
            self.console.ensureCursorVisible()

    def start_or_abort_attack(self):
        if self.worker and self.worker.isRunning():
            self.log_console("\n[SYSTEM] Received Abort Signal. Terminating backend...\n")
            self.worker.stop()
            return

        pdf = self.txt_pdf.text().strip()
        if not pdf:
            self.log_console("\n[ERROR] Target PDF missing.\n")
            return

        # Pre-validate encryption before starting attack thread
        import cracker
        status, _, detail = cracker.check_pdf_encryption(pdf)
        if status == "NOT_ENCRYPTED":
            self.log_console("\n[NOTICE] Attack Aborted: Target PDF has no password protection.\n")
            popup = HackerPopup(
                "PDF NOT ENCRYPTED",
                "This PDF file does NOT have any password protection.\n\nIt is already unlocked and can be opened directly.",
                status="info",
                parent=self
            )
            popup.exec_()
            return

        if status == "UNSUPPORTED":
            self.log_console(f"\n[WARN] {detail}\n")
            popup = HackerPopup(
                "UNSUPPORTED FORMAT",
                f"This PDF uses a non-standard or proprietary security handler.\n\n{detail}",
                status="warn",
                parent=self
            )
            popup.exec_()
            return

        if status == "ERROR":
            self.log_console(f"\n[ERROR] Could not read target PDF: {detail}\n")
            popup = HackerPopup("INVALID PDF", f"Unable to read or parse the PDF:\n\n{detail}", status="error", parent=self)
            popup.exec_()
            return

        is_wordlist = self.radio_wordlist.isChecked()
        wl = self.txt_wordlist.text().strip() if is_wordlist else None
        dg = self.txt_digits.text().strip() if not is_wordlist else None

        if is_wordlist and not wl:
            self.log_console("\n[ERROR] Dictionary missing.\n")
            return

        if not is_wordlist and not dg:
            self.log_console("\n[ERROR] Digit length missing.\n")
            return

        # Toggle UI to ABORT state
        self.btn_attack.setText("ABORT ATTACK")
        self.progress.show()

        self.worker = CrackerWorker(pdf, wl, dg)
        self.worker.output_signal.connect(self.log_console)
        self.worker.finished_signal.connect(self.on_success)
        self.worker.failed_signal.connect(self.on_fail)
        self.worker.error_signal.connect(self.on_error)
        self.worker.start()

    def reset_ui(self):
        self.btn_attack.setEnabled(True)
        self.btn_attack.setText("INITIATE CRACK")
        self.btn_attack.setStyleSheet("background-color: #330000; color: #FF003C; border: 1px solid #FF003C;")
        self.progress.hide()

    def on_success(self, password, time_taken):
        m = f"\n\n=======================================\n[WIN] PASSWORD FOUND: {password}\n[WIN] Time: {time_taken:.2f}s\n=======================================\n"
        self.log_console(m)
        self.reset_ui()
        popup = HackerPopup("CRITICAL SUCCESS", f"Target Decrypted Successfully.\n\nPassword: {password}\nTime: {time_taken:.2f}s", status="success", parent=self)
        popup.exec_()

    def on_fail(self, time_taken):
        self.log_console(f"\n[FAIL] Password Not Found. Time: {time_taken:.2f}s\n")
        self.reset_ui()
        popup = HackerPopup("MISSION FAILED", f"Exhausted attack vector.\nPassword not found in dictionary/range.\nTime: {time_taken:.2f}s", status="error", parent=self)
        popup.exec_()

    def on_error(self, err):
        self.log_console(f"\n[ABORT] {err}\n")
        self.reset_ui()
        if "Abort" not in err:
            if "no password encryption" in str(err).lower():
                popup = HackerPopup(
                    "PDF NOT ENCRYPTED",
                    "This PDF file does NOT have any password protection.\n\nIt is already unlocked and can be opened directly.",
                    status="info",
                    parent=self
                )
            else:
                popup = HackerPopup("SYSTEM ERROR", str(err), status="error", parent=self)
            popup.exec_()

    def animate_title(self):
        import random
        if self.current_title_len < len(self.final_title):
            confirmed = self.final_title[:self.current_title_len]
            target_char = self.final_title[self.current_title_len]
            if target_char == ' ':
                self.current_title_len += 1
                display_text = confirmed + ' '
            else:
                glitch_char = random.choice("!@#$%^&*<>/?0101")
                display_text = confirmed + glitch_char
                self.current_title_len += 1
            
            parts = display_text.split(' ', 1)
            p1 = parts[0]
            p2 = parts[1] if len(parts) > 1 else ""
            decode_html = (
                f"<div align='center' style='line-height: 125%; font-family: \"Segoe UI\", Arial, sans-serif;'>"
                f"<span style='font-size: 22px; font-weight: 900; color: #FFFFFF; letter-spacing: 2.5px;'>{p1}</span><br>"
                f"<span style='font-size: 14px; font-weight: 800; color: #00FF41; letter-spacing: 1.8px;'>{p2}</span>"
                f"</div>"
            )
            self.title_lbl.setText(decode_html)
        else:
            # Done decoding -> Lock in permanent bold typography
            self.title_lbl.setText(self.final_title_html)
            self.title_timer.stop()

    def create_circular_avatar(self, image_path, size=50):
        source = QPixmap(image_path)
        if source.isNull():
            return QPixmap()

        target = QPixmap(size, size)
        target.fill(Qt.transparent)

        painter = QPainter(target)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        # Circular clip for image
        clip_path = QPainterPath()
        clip_path.addEllipse(2, 2, size - 4, size - 4)
        painter.setClipPath(clip_path)

        scaled = source.scaled(size - 4, size - 4, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        x = (size - 4 - scaled.width()) // 2 + 2
        y = (size - 4 - scaled.height()) // 2 + 2
        painter.drawPixmap(x, y, scaled)

        # Glowing Neon Green Ring
        painter.setClipping(False)
        pen = QPen(QColor("#00FF41"))
        pen.setWidthF(1.8)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(2, 2, size - 4, size - 4)
        painter.end()

        return target

