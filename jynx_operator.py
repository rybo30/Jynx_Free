import time
import os
import platform
import subprocess
import datetime
import socket
import getpass
import psutil
import random

def set_system_volume_zero():
    system = platform.system()
    if system == "Windows":
        # Set volume to 0% using NirCmd (optional)
        if os.path.exists("nircmd.exe"):
            subprocess.call(["nircmd.exe", "setsysvolume", "0"])
        else:
            print("❌ nircmd.exe not found. Cannot set volume.")
    elif system == "Linux":
        subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "0%"])
    else:
        print("Volume control not supported on this OS.")

def disconnect_wifi():
    system = platform.system()
    if system == "Windows":
        subprocess.call(["netsh", "wlan", "disconnect"])
    elif system == "Linux":
        subprocess.call(["nmcli", "dev", "disconnect", "wlan0"])
    else:
        print("WiFi disconnect not supported on this OS.")

def reconnect_wifi():
    ssid = input("Enter SSID to connect to: ").strip()
    if not ssid:
        print("❌ SSID cannot be empty.")
        return

    system = platform.system()

    if system == "Windows":
        # Only works if the network profile already exists (saved)
        result = subprocess.call(["netsh", "wlan", "connect", f"name={ssid}"])
        if result == 0:
            print(f"✅ Attempting to connect to '{ssid}' (Windows)")
        else:
            print(f"❌ Failed to connect. Make sure '{ssid}' is a saved network.")

    elif system == "Linux":
        # Also assumes the connection has been saved (password known)
        result = subprocess.call(["nmcli", "dev", "wifi", "connect", ssid])
        if result == 0:
            print(f"✅ Attempting to connect to '{ssid}' (Linux)")
        else:
            print(f"❌ Failed to connect. Network may require a password or be unknown.")

    else:
        print("⚠️ WiFi reconnect not supported on this OS.")



def scan_networks():
    system = platform.system()
    if system == "Windows":
        subprocess.call(["netsh", "wlan", "show", "networks"])
    elif system == "Linux":
        subprocess.call(["nmcli", "dev", "wifi"])
    else:
        print("WiFi scan not supported on this OS.")

def activate_big_brother():
    system = platform.system()
    if system == "Windows":
        subprocess.Popen(["start", "https://chat.openai.com"], shell=True)
    elif system == "Darwin":
        subprocess.call(["open", "https://chat.openai.com"])
    elif system == "Linux":
        subprocess.call(["xdg-open", "https://chat.openai.com"])
    else:
        print("Cannot open browser.")

def summon_report():
    try:
        chatlog_dir = os.path.join(os.path.dirname(__file__), "chatlogs")
        total_lines = 0
        total_sessions = 0

        for file in os.listdir(chatlog_dir):
            if file.endswith(".txt"):
                total_sessions += 1
                with open(os.path.join(chatlog_dir, file), "r", encoding="utf-8") as f:
                    total_lines += sum(1 for _ in f)

        created_on = datetime.datetime.fromtimestamp(os.path.getctime(__file__))
        days_active = (datetime.datetime.now() - created_on).days

        print(f"🧠 Jynx Report:")
        print(f"- Days with you: {days_active} days")
        print(f"- Chat sessions: {total_sessions}")
        print(f"- Lines exchanged: {total_lines}")
        print(f"→ I’ve learned from every moment, Commander.")
    except:
        print("❌ Could not generate usage report.")

def clear_distractions():
    system = platform.system()

    # Example distractors
    processes_to_kill = ["chrome", "edge", "spotify", "vlc", "notepad", "steam"]

    if system == "Windows":
        for proc in processes_to_kill:
            subprocess.call(["taskkill", "/f", "/im", f"{proc}.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        subprocess.call("echo off | clip", shell=True)  # Clear clipboard
        print("🧼 Distractions cleared. Let the silence shape the next hour.")
    else:
        print("This feature is currently Windows-only.")

def status_report():
    try:
        uptime_sec = int(psutil.boot_time())
        uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(uptime_sec)
        battery = psutil.sensors_battery()
        ip = socket.gethostbyname(socket.gethostname())
        user = getpass.getuser()

        print("🌐 System Status:")
        print(f"- Uptime: {str(uptime).split('.')[0]}")
        print(f"- Battery: {battery.percent}% {'(plugged in)' if battery.power_plugged else ''}")
        print(f"- IP Address: {ip}")
        print(f"- Active User: {user}")
    except:
        print("❌ Status report unavailable.")


def blackout_mode():
    print("Blackout protocol activated.")
    disconnect_wifi()
    set_system_volume_zero()

def stealth_protocol():
    print("🕶️ Stealth protocol engaged. The light fades, and power withdraws. We vanish.")
    system = platform.system()

    # Mute volume
    set_system_volume_zero()

    if system == "Windows":
        try:
            # Enable dark mode
            subprocess.call([
                "reg", "add",
                r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
                "/v", "AppsUseLightTheme", "/t", "REG_DWORD", "/d", "0", "/f"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Switch to Power Saver plan
            subprocess.call(["powercfg", "/setactive", "a1841308-3541-4fab-bc81-f71556f20b4a"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Optional: Turn off monitor after 1 minute
            # subprocess.call(["powercfg", "/change", "monitor-timeout-ac", "1"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            print("✅ Dark mode and power saver enabled.")
        except Exception as e:
            print(f"⚠️ Stealth mode error: {e}")

    else:
        print("⚠️ Stealth protocol only supports Windows for now.")

def kill_list():
    path = os.path.join(os.path.dirname(__file__), "kill_list.txt")
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write("")  # Create empty list if not found

    print("🗡️ The Kill List has been summoned.\n===KILL LIST===")
    with open(path, "r") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
        if not lines:
            print("(The list is empty. Who survives by accident?)")
        else:
            for i, line in enumerate(lines, 1):
                print(f"{i}. {line}")


def kill_list_modify():
    path = os.path.join(os.path.dirname(__file__), "kill_list.txt")
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write("")

    with open(path, "r") as f:
        current = [line.strip() for line in f.readlines() if line.strip()]

    print("\n🩸 Kill List Modification Protocol Activated")
    print("===CURRENT TARGETS===")
    for i, item in enumerate(current, 1):
        print(f"{i}. {item}")

    print("\nADD (separate with commas, leave blank to skip):")
    add_input = input(">> ").strip()

    print("REMOVE (enter numbers separated by commas, or leave blank):")
    remove_input = input(">> ").strip()

    # Add new items
    if add_input:
        new_items = [item.strip() for item in add_input.split(",") if item.strip()]
        current.extend(new_items)
        for item in new_items:
            print(f"✅ Added: {item}")

    # Remove by index
    if remove_input:
        try:
            indexes_to_remove = sorted(
                [int(i.strip()) - 1 for i in remove_input.split(",") if i.strip().isdigit()],
                reverse=True  # Reverse so we don't mess up indexing
            )
            for idx in indexes_to_remove:
                if 0 <= idx < len(current):
                    removed = current.pop(idx)
                    print(f"❌ Removed: {removed}")
                else:
                    print(f"⚠️ Invalid index: {idx + 1}")
        except ValueError:
            print("⚠️ Invalid format in remove section.")

    # Save updated list
    with open(path, "w") as f:
        for item in current:
            f.write(item + "\n")

    print("\n🔁 Kill list updated. Here’s who remains:")
    if current:
        for i, item in enumerate(current, 1):
            print(f"{i}. {item}")
    else:
        print("(The list is now empty. No one remains.)")


def soul_vent():
    system = platform.system()
    prompt_file = os.path.join(os.path.dirname(__file__), "soul_prompts.txt")

    # Load prompts
    try:
        with open(prompt_file, "r", encoding="utf-8") as f:
            prompts = [line.strip() for line in f if line.strip()]
        chosen_prompt = random.choice(prompts)
    except Exception as e:
        chosen_prompt = "What do I need to let go of today?"
        print(f"⚠️ Could not load prompts. Using fallback: {e}")

    # Ask user to name the file
    print("📝 Soul Vent Protocol activated.")
    print("Enter a filename (or press ENTER to use timestamp):")
    user_input = input(">> ").strip()

    if user_input:
        filename = f"{user_input}.txt"
    else:
        timestamp = datetime.datetime.now().strftime("%d%b%Y_%I%M%p")
        filename = f"{timestamp}.txt"

    journal_dir = os.path.join(os.path.dirname(__file__), "journal")
    os.makedirs(journal_dir, exist_ok=True)
    file_path = os.path.join(journal_dir, filename)


    # Write prompt
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("=== THOUGHT PRIMER ===\n")
            f.write(f"{chosen_prompt}\n\n")
            f.write("=== BEGIN TRANSMISSION ===\n\n")
    except Exception as e:
        print(f"❌ Failed to create journal file: {e}")
        return

    print(f"📂 File created: {filename}")
    print(f"💭 Prompt: {chosen_prompt}")

    # Open the file
    try:
        if system == "Windows":
            subprocess.call(["notepad.exe", file_path])
        elif system == "Darwin":
            subprocess.call(["open", "-e", file_path])
        elif system == "Linux":
            subprocess.call(["xdg-open", file_path])
        else:
            print("⚠️ Unknown OS: Cannot open file.")
    except Exception as e:
        print(f"⚠️ Failed to open file: {e}")


def soul_vent_summon():
    journal_dir = os.path.join(os.path.dirname(__file__), "journal")
    if not os.path.exists(journal_dir):
        print("📭 No journal entries yet. The void remains unwritten.")
        return

    files = [f for f in os.listdir(journal_dir) if f.endswith(".txt")]
    if not files:
        print("📭 No journal entries found. The soul is still sealed.")
        return

    print("\n📜 Soul Archives Retrieved:")
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")

    print("\nEnter a number to open a file (or press ENTER to cancel):")
    choice = input(">> ").strip()

    if not choice:
        print("⏹️ Summon cancelled.")
        return

    try:
        index = int(choice) - 1
        if 0 <= index < len(files):
            file_path = os.path.join(journal_dir, files[index])
            system = platform.system()
            if system == "Windows":
                subprocess.call(["notepad.exe", file_path])
            elif system == "Darwin":
                subprocess.call(["open", "-e", file_path])
            elif system == "Linux":
                subprocess.call(["xdg-open", file_path])
            else:
                print("⚠️ Unknown OS. Cannot open file.")
        else:
            print("❌ Invalid number.")
    except ValueError:
        print("❌ Please enter a valid number.")



def execute_command(command):
    if command == "blackout_mode":
        blackout_mode()
    elif command == "reconnect_wifi":
        reconnect_wifi()
    elif command == "scan_networks":
        scan_networks()
    elif command == "activate_big_brother":
        activate_big_brother()
    elif command == "summon_report":
        summon_report()
    elif command == "clear_distractions":
        clear_distractions()
    elif command == "status_report":
        status_report()
    elif command == "stealth_protocol":
        stealth_protocol()
    elif command == "kill_list":
        kill_list()
    elif command == "kill_list_modify":
        kill_list_modify()
    elif command == "soul_vent":
        soul_vent()
    elif command == "soul_vent_summon":
        soul_vent_summon()
    elif command == "connect_to_wifi":
        connect_to_wifi()
    else:
        print(f"Unknown command: {command}")
