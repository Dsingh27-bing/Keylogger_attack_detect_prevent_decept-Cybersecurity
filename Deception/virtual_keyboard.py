import subprocess
import tkinter as tk
import random
import string
import threading
import pyautogui
import time
from Quartz.CoreGraphics import CGEventCreateKeyboardEvent, kCGEventKeyDown, kCGEventKeyUp, kCGEventSourceStateHIDSystemState, CGEventPost, kCGEventSourceStateCombinedSessionState
class VirtualKeyboard:
    def __init__(self, master):
        self.master = master
        self.master.title("Virtual Keyboard")

        self.entry = tk.Entry(self.master, font=('Arial', 14))
        self.entry.pack(pady=10)

        self.text_area = tk.Text(self.master, height=10, width=30, font=('Arial', 14))
        self.text_area.pack(pady=10)

        self.create_keyboard()

        # button to send text to the application
        self.send_button = tk.Button(self.master, text="Send to Application", command=self.send_to_application)
        self.send_button.pack(pady=10)
    def simulate_key_press(self, keylogs):
        for key in keylogs:
            pyautogui.press(key)
            time.sleep(0.05)  # Add a small delay (to replicate human like behaviour)
    def post_key_event(self, key_code, key_down=True):
        event_type = kCGEventKeyDown if key_down else kCGEventKeyUp
        event = CGEventCreateKeyboardEvent(None, key_code, event_type)
        CGEventPost(kCGEventSourceStateHIDSystemState, event)

    def create_keyboard(self):
        buttons = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
            ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';'],
            ['z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/']
        ]

        for row in buttons:
            key_frame = tk.Frame(self.master)
            key_frame.pack()

            for key in row:
                btn = tk.Button(key_frame, text=key, width=5, height=2, command=lambda k=key: self.key_press(k))
                btn.pack(side=tk.LEFT)

        # Add 'Space' button separately       
        space_frame = tk.Frame(self.master)
        space_frame.pack()
        space_btn = tk.Button(space_frame, text='Space', width=5, height=2, command=lambda: self.key_press(' '))
        space_btn.pack(side=tk.LEFT)
        # Add 'Return' button separately
        return_frame = tk.Frame(self.master)
        return_frame.pack()
        return_btn = tk.Button(return_frame, text='Return', width=5, height=2, command=lambda: self.key_press('\n'))
        return_btn.pack(side=tk.LEFT)

        # Add 'Delete' button separately
        delete_frame = tk.Frame(self.master)
        delete_frame.pack()
        delete_btn = tk.Button(delete_frame, text='Delete', width=8, height=2, command=self.backspace_press)
        delete_btn.pack(side=tk.LEFT)

    def backspace_press(self):
        current_text = self.entry.get()
        new_text = current_text[:-1]  # remove the last character
        self.entry.delete(0, tk.END)
        self.entry.insert(0, new_text)

        # update the Text widget when Delete is pressed
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, new_text)

    def key_press(self, key):
        current_text = self.entry.get()
        new_text = current_text + key
        self.entry.delete(0, tk.END)
        self.entry.insert(0, new_text)

        # update the Text widget when a key is pressed
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, new_text)

    def send_to_application(self):
        # Get the text to send
        application_text = self.text_area.get("1.0", tk.END).strip()

        # Print the application text (for demonstration purposes), for error handling
        #print("Application Text:", repr(application_text))

        # Generate random keylogs (same length as the application text)
        random_keylogs = [random.choice(string.ascii_letters + string.digits) for _ in range(len(application_text))]

        # Print the random keylogs (for demonstration purposes), for error handling
        #print("Random Keylogs:", random_keylogs)

        # Simulate key presses using Quartz
        threading.Thread(target=self.simulate_key_press, args=(random_keylogs,), daemon=True).start()


        # using AppleScript to write to TextEdit application
        script = f'tell application "TextEdit" to set text of front document to "{application_text}"'
        subprocess.run(['osascript', '-e', script], check=True)

        # run keylogger detection
        self.run_keylogger_detection()

        # Clear the text area after sending the text
        self.entry.delete(0, tk.END)
        self.text_area.delete("1.0", tk.END)

    def run_keylogger_detection(self):
        try:
            completed_process = subprocess.run(["sudo", "python3", "detection.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            print("Detection script output:")
            print(completed_process.stdout)
            print(completed_process.stderr)
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    keyboard_app = VirtualKeyboard(root)
    root.mainloop()
