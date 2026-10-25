import sys
import io
import time
from PyQt5.QtCore import QThread, pyqtSignal

class StreamRedirector(io.StringIO):
    def __init__(self, signal):
        super().__init__()
        self.signal = signal

    def write(self, text):
        if text:
            # Send the text to the GUI thread
            self.signal.emit(text)

    def flush(self):
        pass


class CrackerWorker(QThread):
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str, float)  # password, time taken
    failed_signal = pyqtSignal(float)
    error_signal = pyqtSignal(str)

    def __init__(self, pdf_path, wordlist_path=None, digits=None):
        super().__init__()
        self.pdf_path = pdf_path
        self.wordlist_path = wordlist_path
        self.digits = digits
        self.is_running = True

    def run(self):
        # Redirect stdout to GUI console
        original_stdout = sys.stdout
        sys.stdout = StreamRedirector(self.output_signal)

        start_time = time.time()
        found_password = None
        attack_executed = False

        try:
            # Import cracker locally so it picks up the redirected stdout
            import cracker
            import os

            self.output_signal.emit("[SYSTEM] Initializing Cracker Engine...\n")

            # Check and Extract Hash
            status, hash_str, detail = cracker.check_pdf_encryption(self.pdf_path)
            hash_file = os.path.join(cracker.SCRIPT_DIR, "hash.txt")

            if status == "NOT_ENCRYPTED":
                self.output_signal.emit("[NOTICE] Target PDF is NOT password protected. File is already unlocked.\n")
                self.error_signal.emit("Target PDF has no password encryption.")
                return
            elif status == "UNSUPPORTED":
                self.output_signal.emit(f"[ERROR] Unsupported encryption: {detail}\n")
                self.error_signal.emit(f"Unsupported encryption: {detail}")
                return
            elif status != "ENCRYPTED" or not hash_str:
                self.output_signal.emit(f"[ERROR] Could not read PDF: {detail}\n")
                self.error_signal.emit(f"PDF read error: {detail}")
                return

            with open(hash_file, "w") as hf:
                hf.write(hash_str + "\n")
            self.output_signal.emit(f"[INFO] Hash extracted! Algo: {detail}\n")

            john_exe = cracker.find_john()
            if not john_exe and sys.platform != "win32":
                self.output_signal.emit("[NOTICE] John the Ripper not found on this Linux system.\n")
                self.output_signal.emit("[SYSTEM] Initiating automatic installation via package manager...\n")
                success = cracker.install_linux_john(output_callback=self.output_signal.emit)
                if success:
                    john_exe = cracker.find_john()
                    self.output_signal.emit(f"[SUCCESS] John the Ripper installed successfully! ({john_exe})\n\n")
                else:
                    self.output_signal.emit("[ERROR] Automatic installation failed or was cancelled.\n")
                    self.output_signal.emit("[HINT] Please install manually by running: sudo apt install john\n")
                    self.error_signal.emit("John the Ripper missing on Linux.")
                    return

            if not john_exe:
                self.output_signal.emit("[ERROR] John the Ripper not found in backend.\n")
                self.error_signal.emit("John missing")
                return

            cracker.clear_john_pot(john_exe, hash_file)

            # Attack Logic
            attack_executed = True
            if self.wordlist_path:
                self.output_signal.emit(f"[INFO] Starting Wordlist Attack...\n")
                found_password = cracker.run_john(
                    john_exe, hash_file, wordlist=self.wordlist_path, stop_check=lambda: self.is_running
                )
            elif self.digits:
                self.output_signal.emit(f"[INFO] Starting Dynamic Digits Attack ({self.digits})...\n")
                if "-" in self.digits:
                    min_len, max_len = map(int, self.digits.split("-"))
                else:
                    min_len = max_len = int(self.digits)
                    
                for length in range(min_len, max_len + 1):
                    if not self.is_running:
                        break
                    mask = "?d" * length
                    self.output_signal.emit(f"\n[INFO] Trying {length}-digit combinations...\n")
                    found_password = cracker.run_john(
                        john_exe, hash_file, mask=mask, stop_check=lambda: self.is_running
                    )
                    if found_password:
                        break

            # Cleanup
            if os.path.isfile(hash_file):
                try:
                    os.remove(hash_file)
                except:
                    pass

        except Exception as e:
            self.output_signal.emit(f"\n[FATAL ERROR] {str(e)}\n")
            self.error_signal.emit(str(e))
        finally:
            # Restore stdout
            sys.stdout = original_stdout

            elapsed = time.time() - start_time
            if found_password:
                self.finished_signal.emit(found_password, elapsed)
            elif attack_executed:
                if self.is_running:
                    self.failed_signal.emit(elapsed)
                else:
                    self.error_signal.emit("Attack Aborted by User")

    def stop(self):
        self.is_running = False
        try:
            import cracker
            cracker.abort_current_run()
        except Exception:
            pass

