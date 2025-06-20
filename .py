import tkinter as tk
import random
import threading
import time

POPUP_INTERVAL = 0.1  # seconds between popup spawns (roughly)
closed_popups_count = 0
closed_popups_lock = threading.Lock()
decode_popup_shown = False
countdown_active = True  # True while countdown runs
virus_running = True  # Controls popup spawning loop

# Global control to restart simulation
restart_simulation_flag = threading.Event()

def rot13(text):
    return text.translate(str.maketrans(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm"
    ))

def show_random_popup():
    global closed_popups_count, decode_popup_shown, countdown_active, virus_running

    window = tk.Tk()
    window.title("Virus Alert!")
    window.geometry(f"350x200+{random.randint(0, 1000)}+{random.randint(0, 800)}")
    window.attributes("-topmost", True)

    messages = [
        "UNKNOWN (ROT13 CIPHER)",
        "UNKNOWN detected! (ROT13 CIPHER)",
        "System compromised by UNKNOWN! (ROT13 CIPHER)",
        "ALERT: UNKNOWN breach detected! (ROT13 CIPHER)",
        "Security risk: UNKNOWN in system! (ROT13 CIPHER)",
        "UNKNOWN malware spreading rapidly! (ROT13 CIPHER)",
        "System error due to UNKNOWN! (ROT13 CIPHER)"
    ]
    message = random.choice(messages)

    text = tk.Text(window, wrap='word', font=("Arial", 14), height=4, width=40)
    text.tag_configure("highlight", foreground="red", font=("Arial", 14, "bold"))
    text.tag_configure("rot13", foreground="blue", font=("Arial", 12, "underline"))
    text.tag_configure("center", justify="center")

    start_index = message.find("UNKNOWN")
    rot13_index = message.find("(ROT13 CIPHER)")

    if start_index != -1 and rot13_index != -1:
        text.insert("1.0", message[:start_index])
        text.insert("end", "UNKNOWN", ("highlight",))
        text.insert("end", message[start_index+7:rot13_index])
        text.insert("end", "(ROT13 CIPHER)", ("rot13",))
        text.insert("end", message[rot13_index+13:])
    else:
        text.insert("1.0", message)

    text.tag_add("center", "1.0", "end")
    text.configure(state='disabled')
    text.pack(expand=True, fill='both')

    decoded_label = tk.Label(window, text="", fg="green", font=("Arial", 12))
    decoded_label.pack()

    def decode_rot13(event=None):
        decoded = rot13("UNKNOWN")
        decoded_label.config(text=f"UNKNOWN decoded is: {decoded}")

    text.tag_bind("rot13", "<Button-1>", decode_rot13)

    def on_close():
        global closed_popups_count, decode_popup_shown, virus_running
        with closed_popups_lock:
            closed_popups_count += 1
            if not countdown_active and closed_popups_count >= 3 and not decode_popup_shown:
                decode_popup_shown = True
                virus_running = False
                threading.Thread(target=show_decode_popup).start()
        window.destroy()

    close_button = tk.Button(window, text="Close", command=on_close)
    close_button.pack(pady=5)

    window.after(random.randint(3000, 7000), window.destroy)
    window.mainloop()

def show_decode_popup():
    global decode_popup_shown, closed_popups_count, countdown_active, virus_running

    correct_answer = rot13("UNKNOWN")

    decode_win = tk.Tk()
    decode_win.title("Decode the message")
    decode_win.geometry("400x180")
    decode_win.attributes("-topmost", True)

    def disable_event():
        pass
    decode_win.protocol("WM_DELETE_WINDOW", disable_event)

    label = tk.Label(decode_win, text="Manually decode the word 'UNKNOWN' using ROT13:", font=("Arial", 12))
    label.pack(pady=10)

    entry = tk.Entry(decode_win, font=("Arial", 14))
    entry.pack(pady=5)

    result_label = tk.Label(decode_win, text="", font=("Arial", 12))
    result_label.pack(pady=5)

    def check_decode():
        user_input = entry.get().strip()
        if user_input.upper() == correct_answer.upper():
            result_label.config(text="Correct! Thank you.", fg="green")
            decode_win.after(1000, decode_win.destroy)
        else:
            result_label.config(text="Incorrect. Restarting popups.", fg="red")
            entry.delete(0, tk.END)
            decode_win.after(1000, decode_win.destroy)
            # Restart popups
            threading.Thread(target=virus_simulation_loop).start()

    submit_btn = tk.Button(decode_win, text="Submit", command=check_decode)
    submit_btn.pack(pady=10)

    decode_win.mainloop()

def virus_simulation_loop():
    global virus_running, closed_popups_count, decode_popup_shown, countdown_active

    while True:
        # Reset simulation state
        closed_popups_count = 0
        decode_popup_shown = False
        countdown_active = True
        virus_running = True

        restart_simulation_flag.clear()

        # Start simulation and countdown
        popup_thread = threading.Thread(target=virus_simulation, daemon=True)
        popup_thread.start()
        countdown_thread = threading.Thread(target=countdown_timer, args=(15,), daemon=True)
        countdown_thread.start()

        # Wait until restart_simulation_flag is set (user failed)
        restart_simulation_flag.wait()

        # Stop popups
        virus_running = False
        print("🔁 Restarting virus simulation...")

def virus_simulation():
    global virus_running
    while virus_running:
        time.sleep(random.uniform(POPUP_INTERVAL / 2, POPUP_INTERVAL * 1.5))
        if not virus_running:
            break
        threading.Thread(target=show_random_popup).start()

def countdown_timer(seconds=15):
    global countdown_active
    for i in range(seconds, 0, -1):
        print(f"⏳ Countdown: {i} seconds left")
        time.sleep(1)
    print("⏰ Countdown ended! Popups still running...")
    countdown_active = False

if __name__ == "__main__":
    # Main loop that restarts simulation as needed
    virus_simulation_loop()
