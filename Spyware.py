# Imports
import keyboard
import time
import win32gui
from pynput import mouse
from threading import Thread
from collections import deque
import os

# Get the current time and format it
formatted_time = time.strftime("%Y-%m-%d %H:%M:%S")
key_batch = deque()
batch_size = 6  # Number of keys to batch together

# Define the log directory path
Log_Directory = "Data-Log/Tracker"

# Create the directory if it doesn't exist
if not os.path.exists(Log_Directory):
    os.makedirs(Log_Directory)

# Define paths for log files inside the directory
keyboard_log_path = os.path.join(Log_Directory, "DataLogKeyboard.txt")
mouse_log_path = os.path.join(Log_Directory, "DataLogMouse.txt")

def get_active_window():
    """Get the title of the currently active window."""
    try:
        # Attempt to retrieve the title of the active window
        return win32gui.GetWindowText(win32gui.GetForegroundWindow())
    except win32gui.error as e:  # Catch specific win32gui errors
        print(f"Error fetching active window: {e}")  # Log the error for debugging
        return "Unknown Window"
    except Exception as e:  # Handle unexpected exceptions, but log them
        print(f"Unexpected error: {e}")  # Log unexpected exceptions
        return "Unknown Window"

def mouse_datalog(x, y, button, pressed):
    """Log mouse activity to a file."""
    action = "pressed" if pressed else "released"
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

    with open(mouse_log_path, "w") as f:  # Use 'a' to append data to the file
        f.write(f"{timestamp} - Button {button} {action} at ({x}, {y})\n")
    print(f"{timestamp} - Button {button} {action} at ({x}, {y})")  # Debug print

def monitor_mouse_clicks():
    """Monitor and log mouse clicks."""
    with mouse.Listener(on_click=mouse_datalog) as listener:
        listener.join()

def init_keyboard_datalog():
    """Initialize the keyboard log file with a header."""
    with open(keyboard_log_path, "w") as f:  # Use 'w' to create/reset the file
        f.write(f"Logging Data as of: {formatted_time}\n")
        f.write("====================================\n")

def log_key_batch():
    """Log a batch of keys to the keyboard log file."""
    global key_batch
    if key_batch:
        with open(keyboard_log_path, "w") as f:
            batch_data = ''.join(key_batch)  # Combine the deque into a string
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            active_window = get_active_window()
            f.write(f"{timestamp} [Window: {active_window}] - Keys: {batch_data}\n")
        key_batch.clear()  # Clear the deque after logging

def monitor_keys():
    """Monitor and log key presses."""
    print("Press 'esc' to stop logging.")
    try:
        while True:
            # Listen for a key press event
            event = keyboard.read_event()

            if event.event_type == keyboard.KEY_DOWN:
                if len(event.name) == 1 or event.name in ["space", "enter"]:  # Only log single-character keys
                    key_batch.append(event.name)
                    print(f"Captured key: {event.name}")  # Debug print

                if len(key_batch) >= batch_size:  # Log when the batch is full
                    log_key_batch()

            if event.name == "esc":  # Exit condition
                print("Exiting program.")
                break
    finally:
        log_key_batch()  # Ensure remaining keys are logged before exit

if __name__ == "__main__":
    print("Tracker is up and running... [INFO] Directory Named: Data-Log/Tracker Containing Data Logs from Mouse and Keyboard Movement Was Generated!")
    # Initialize log files
    init_keyboard_datalog()

    # Run both keyboard and mouse monitoring in separate threads
    mouse_thread = Thread(target=monitor_mouse_clicks, daemon=True)
    keyboard_thread = Thread(target=monitor_keys, daemon=False)

    mouse_thread.start()
    keyboard_thread.start()

    # Wait for the keyboard thread to finish (it stops on 'esc')
    keyboard_thread.join()
    print("Logging stopped.")
