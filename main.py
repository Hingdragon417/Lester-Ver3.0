import sys
import time
import pynput
import ctypes
import tkinter as tk
from queue import Empty, Queue
from threading import Thread
from win32gui import FindWindow, GetWindowRect
from hacks import bruteforce, casinofingerprint, casinokeypad, cayofingerprint, cayovoltage, hostnumber

VERSION = "Lester-VER3.0"
OVERLAY_MS = 7000

KEYBINDS = [
    ("F4", "Exit"),
    ("F5", "Fingerprint Scanner"),
    ("F6", "Keypad Cracker"),
    ("F7", "Retro Fingerprint Scanner"),
    ("F8", "Voltage Hack"),
    ("F9", "Host Number Matcher"),
    ("F10", "BruteForce Matcher"),
]

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def print_banner():
    print(f'''
 _        _______  _______ _________ _______  _______
( \      (  ____ \(  ____ \\__   __/(  ____ \(  ____ )
| (      | (    \/| (    \/   ) (   | (    \/| (    )|
| |      | (__    | (_____    | |   | (__    | (____)|
| |      |  __)   (_____  )   | |   |  __)   |     __)
| |      | (            ) |   | |   | (      | (\ (
| (____/\| (____/\/\____) |   | |   | (____/\| ) \ \__
(_______/(_______/\_______)   )_(   (_______/|/   \__/

                      {VERSION}
''')

def print_credits():
    print('''
Made by JUSTDIE
Special thanks to RedHeadEmile
    ''')

class KeybindOverlay:
    def __init__(self):
        self.queue = Queue()
        self.thread = Thread(target=self._run, daemon=True)
        self.thread.start()

    def show(self):
        self.queue.put("show")

    def _run(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.after(50, self._process_queue)
        self.root.mainloop()

    def _build_window(self):
        self.window = tk.Toplevel(self.root)
        self.window.withdraw()
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.attributes("-alpha", 0.9)
        self.window.configure(bg="#101114")

        title = tk.Label(
            self.window,
            text="Lester Keybinds",
            bg="#101114",
            fg="#f2f2f2",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        )
        title.pack(fill="x", padx=12, pady=(10, 4))

        for key, label in KEYBINDS:
            row = tk.Frame(self.window, bg="#101114")
            row.pack(fill="x", padx=12, pady=1)

            key_label = tk.Label(
                row,
                text=key,
                width=4,
                bg="#22262c",
                fg="#ffffff",
                font=("Segoe UI", 9, "bold"),
                padx=4,
                pady=2,
            )
            key_label.pack(side="left")

            action_label = tk.Label(
                row,
                text=label,
                bg="#101114",
                fg="#d6d6d6",
                font=("Segoe UI", 9),
                anchor="w",
            )
            action_label.pack(side="left", padx=(8, 0))

        hint = tk.Label(
            self.window,
            text="/  show this reminder",
            bg="#101114",
            fg="#9ca3af",
            font=("Segoe UI", 8),
            anchor="w",
        )
        hint.pack(fill="x", padx=12, pady=(6, 10))

    def _position_window(self):
        width = 245
        height = 220
        x = self.root.winfo_screenwidth() - width - 18
        y = 18
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def _process_queue(self):
        try:
            while True:
                command = self.queue.get_nowait()
                if command == "show":
                    self._show_window()
        except Empty:
            pass

        self.root.after(50, self._process_queue)

    def _show_window(self):
        if not hasattr(self, "window"):
            self._build_window()

        if hasattr(self, "hide_job"):
            self.root.after_cancel(self.hide_job)

        self._position_window()
        self.window.deiconify()
        self.window.lift()
        self.window.attributes("-topmost", True)
        self.hide_job = self.root.after(OVERLAY_MS, self.window.withdraw)

def check_window():
    print('[*] Searching Grand Theft Auto V...')

    while True:
        hwnd = FindWindow(None, "Grand Theft Auto V")

        if hwnd:
            print('[*] Grand Theft Auto V Detected!')
            print('')
            print('=============================================')
            return GetWindowRect(hwnd)

        time.sleep(1)

def casino_fingerprint(bbox):
    thread = Thread(target=casinofingerprint.main, args=(bbox,))
    thread.start()

def casino_keypad(bbox):
    thread = Thread(target=casinokeypad.main, args=(bbox,))
    thread.start()

def cayo_fingerprint(bbox):
    thread = Thread(target=cayofingerprint.main, args=(bbox,))
    thread.start()

def cayo_voltage(bbox):
    thread = Thread(target=cayovoltage.main, args=(bbox,))
    thread.start()

def host_number(bbox):
    thread = Thread(target=hostnumber.main, args=(bbox,))
    thread.start()

def brute_force(bbox):
    thread = Thread(target=bruteforce.main, args=(bbox,))
    thread.start()

def shutdown():
    sys.exit()

def main():
    print_banner()
    print_credits()

    overlay = KeybindOverlay()
    bbox = check_window()
    if bbox:
        with pynput.keyboard.GlobalHotKeys({
                '<F4>': shutdown,
                '<F5>': lambda: casino_fingerprint(bbox),
                '<F6>': lambda: casino_keypad(bbox),
                '<F7>': lambda: cayo_fingerprint(bbox),
                '<F8>': lambda: cayo_voltage(bbox),
                '<F9>': lambda: host_number(bbox),
                '<F10>': lambda: brute_force(bbox),
                '/': overlay.show}) as h:
            h.join()

if __name__ == "__main__":
    ctypes.windll.user32.SetProcessDPIAware()
    main()
