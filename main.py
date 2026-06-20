import sys
import time
import os
import pynput
import ctypes
import hashlib
import json
import subprocess
import tempfile
import tkinter as tk
import urllib.request
from queue import Empty, Queue
from threading import Thread
from win32gui import FindWindow, GetWindowRect
from hacks import bruteforce, casinofingerprint, casinokeypad, cayofingerprint, cayovoltage, hostnumber

VERSION = "Lester-VER3.0"
OVERLAY_MS = 7000
REPO_OWNER = "Hingdragon417"
REPO_NAME = "Lester-Ver3.0"
REPO_BRANCH = "main"
GITHUB_API_COMMIT = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits/{REPO_BRANCH}"
RAW_EXE_URL = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{REPO_BRANCH}/dist/Lester-Ver3.0.exe"

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

def message_box(message, title=VERSION, flags=0x40):
    return ctypes.windll.user32.MessageBoxW(None, message, title, flags)

def ask_yes_no(message, title=VERSION):
    return message_box(message, title, 0x24) == 6

def app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)

    return os.path.dirname(os.path.abspath(__file__))

def request_url(url):
    request = urllib.request.Request(url, headers={'User-Agent': VERSION})
    with urllib.request.urlopen(request, timeout=8) as response:
        return response.read()

def latest_remote_commit():
    data = json.loads(request_url(GITHUB_API_COMMIT).decode('utf-8'))
    return data.get('sha'), data.get('commit', {}).get('message', '')

def current_git_commit(root):
    try:
        return subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'],
            cwd=root,
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
    except Exception:
        return None

def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b''):
            digest.update(chunk)

    return digest.hexdigest()

def download_latest_exe():
    fd, path = tempfile.mkstemp(prefix='Lester-Ver3.0-update-', suffix='.exe')
    os.close(fd)

    with urllib.request.urlopen(
            urllib.request.Request(RAW_EXE_URL, headers={'User-Agent': VERSION}),
            timeout=30) as response:
        with open(path, 'wb') as file:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                file.write(chunk)

    return path

def restart_current_process(root):
    subprocess.Popen([sys.executable] + sys.argv, cwd=root)
    sys.exit()

def update_source_checkout(root, latest_sha):
    if not ask_yes_no(
            f"A new version is available on GitHub.\n\nLatest: {latest_sha[:7]}\n\nUpdate now?"):
        return

    try:
        subprocess.check_call(['git', 'pull', '--ff-only', 'origin', REPO_BRANCH], cwd=root)
    except Exception as e:
        message_box(f"Update failed:\n\n{e}", flags=0x10)
        return

    message_box("Update complete. Lester will restart now.")
    restart_current_process(root)

def update_packaged_exe(current_exe, latest_sha):
    update_exe = None
    try:
        update_exe = download_latest_exe()
        if sha256_file(current_exe) == sha256_file(update_exe):
            os.remove(update_exe)
            return

        if not ask_yes_no(
                f"A new version is available on GitHub.\n\nLatest push: {latest_sha[:7]}\n\nDownload and install it now?"):
            os.remove(update_exe)
            return

        script_path = os.path.join(tempfile.gettempdir(), 'update-lester.cmd')
        with open(script_path, 'w') as script:
            script.write('@echo off\n')
            script.write('timeout /t 2 /nobreak >nul\n')
            script.write(f'copy /Y "{update_exe}" "{current_exe}" >nul\n')
            script.write(f'start "" "{current_exe}"\n')
            script.write(f'del "{update_exe}" >nul 2>nul\n')
            script.write('del "%~f0" >nul 2>nul\n')

        message_box("Update downloaded. Lester will restart now.")
        subprocess.Popen(
            ['cmd', '/c', script_path],
            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)
        )
        sys.exit()
    except Exception as e:
        if update_exe and os.path.exists(update_exe):
            os.remove(update_exe)
        message_box(f"Update check failed:\n\n{e}", flags=0x10)

def check_for_updates():
    try:
        latest_sha, _ = latest_remote_commit()
        if not latest_sha:
            return

        root = app_dir()
        local_sha = current_git_commit(root)
        if local_sha and local_sha != latest_sha:
            update_source_checkout(root, latest_sha)
            return

        if getattr(sys, 'frozen', False):
            update_packaged_exe(sys.executable, latest_sha)
    except Exception as e:
        print(f'[!] Update check skipped: {e}')

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
    check_for_updates()

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
