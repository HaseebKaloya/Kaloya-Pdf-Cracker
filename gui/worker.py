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

        try:
            # Import cracker locally so it picks up the redirected stdout
            import cracker
            import os

            self.output_signal.emit("[SYSTEM] Initializing Cracker Engine...\n")

            # Extract Hash
            hash_str, algo = cracker.extract_pdf_info(self.pdf_path)
            hash_file = os.path.join(cracker.SCRIPT_DIR, "hash.txt")

            if hash_str:
                with open(hash_file, "w") as hf:
                    hf.write(hash_str + "\n")
                self.output_signal.emit(f"[INFO] Hash extracted! Algo: {algo}\n")
            else:
                self.output_signal.emit("[ERROR] Could not extract hash. Is it encrypted?\n")
                self.error_signal.emit("Hash extraction failed")
                sys.stdout = original_stdout
                return

            john_exe = cracker.find_john()
            if not john_exe:
                self.output_signal.emit("[ERROR] John the Ripper not found in backend.\n")
                self.error_signal.emit("John missing")
                sys.stdout = original_stdout
                return

            cracker.clear_john_pot(john_exe, hash_file)

            # Attack Logic
            if self.wordlist_path:
                self.output_signal.emit(f"[INFO] Starting Wordlist Attack...\n")
                found_password = cracker.run_john(john_exe, hash_file, wordlist=self.wordlist_path)
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
                    found_password = cracker.run_john(john_exe, hash_file, mask=mask)
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
            else:
                if self.is_running:
                    self.failed_signal.emit(elapsed)
                else:
                    self.error_signal.emit("Attack Aborted by User")

    def stop(self):
        self.is_running = False
