import os
import sys
import subprocess
import tkinter as tk
import threading
from pynput import keyboard as kb
import nice_errors  # optional for better errors
from elevate_updated import elevate

def is_root():
    return os.getuid() == 0

PF_RULES_FILE = "/tmp/lagswitch_block_all.conf"

def create_pf_rules():
    rules = """
    block drop out proto tcp from any to any
    """
    with open(PF_RULES_FILE, "w") as f:
        f.write(rules)

def enable_lag():
    create_pf_rules()
    subprocess.run(["pfctl", "-f", PF_RULES_FILE])
    subprocess.run(["pfctl", "-e"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def disable_lag():
    subprocess.run(["pfctl", "-d"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def toggle_lag(state_label, status):
    if status["enabled"]:
        disable_lag()
        state_label.config(text="Lag OFF", fg="green")
        status["enabled"] = False
    else:
        enable_lag()
        state_label.config(text="Lag ON", fg="red")
        status["enabled"] = True

def listen_hotkeys(state_label, status):
    def on_press(key):
        try:
            if key.char == '=':
                toggle_lag(state_label, status)
        except AttributeError:
            pass

    with kb.Listener(on_press=on_press) as listener:
        listener.join()

def main_gui():
    status = {"enabled": False}

    root = tk.Tk()
    root.title("Lag Switch")
    root.geometry("240x120")

    label = tk.Label(root, text="Lag OFF", fg="green", font=("Helvetica", 18))
    label.pack(pady=10)

    toggle_button = tk.Button(root, text="Toggle Lag", command=lambda: toggle_lag(label, status))
    toggle_button.pack(pady=5)

    info_label = tk.Label(root, text="[=] Toggle Lag", font=("Helvetica", 10))
    info_label.pack(pady=5)

    threading.Thread(target=listen_hotkeys, args=(label, status), daemon=True).start()
    root.mainloop()

if __name__ == "__main__":
    if not is_root():
        try:
            elevate()
            print("Elevation succeeded. Exiting current process.")
            sys.exit(0)
        except:
            print("Failed to elevate privileges")
            sys.exit(1)

    if is_root():
        main_gui()
        disable_lag()
    print("done")
    quit()
