import os
import select
import subprocess
import sys
import termios
import time
import tty

from utils import debounce
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class ChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.handle_change = debounce(wait_ms=1000)(self._handle_change)

    def on_any_event(self, event):
        if event.is_directory:
            return
        elif event.event_type in ["created", "modified", "deleted"]:
            file_extension = os.path.splitext(event.src_path)[1]
            if file_extension in [".py", ".sql", ".json"]:
                self.handle_change(event.src_path)

    def _handle_change(self, file_path):
        print(f"Detected change in {file_path}. Restarting...")
        restart_process()


@debounce(wait_ms=100)
def restart_process():
    global process
    if process:
        process.terminate()
        process.wait()
    process = subprocess.Popen([sys.executable, "main.py"])
    print("Process restarted.")


def check_manual_reload():
    if select.select([sys.stdin], [], [], 0.0)[0]:
        key = sys.stdin.read(1)
        if key == "r":
            print("Manual reload triggered.")
            restart_process()
            return True
    return False

if __name__ == "__main__":
    process = None
    restart_process()

    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=True)
    observer.start()

    if os.isatty(sys.stdin.fileno()):
        # Terminal-specific code
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setcbreak(sys.stdin.fileno())

            print("Watcher started. Press 'r' to manually reload.")
            while True:
                if check_manual_reload():
                    continue
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nStopping watcher...")
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    else:
        # Non-terminal environment (e.g., Docker container)
        print("Watcher started. Manual reload not available in this environment.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping watcher...")

    observer.stop()
    observer.join()

    if process:
        process.terminate()
        process.wait()