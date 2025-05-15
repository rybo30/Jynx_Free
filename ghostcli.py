import os
import getpass
import datetime
import contextlib
import random
import re
import json
import time
from llama_cpp import Llama
from cryptography.fernet import Fernet
from confidence_engine import score_response
from verify_engine import verify_input
from clarity_engine import clarify_response
from jynx_operator import execute_command
from pyfiglet import Figlet
import json

# ===UNIVERSAL VARIABLES AND LISTS===
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BLOCKED_KEYWORDS_FILE = os.path.join(SCRIPT_DIR, "user_memory", "blocked_keywords.json")
CURRENT_DIR = os.getcwd()  # dynamically gets the folder where ghostcli.py is launched
KNOWLEDGE_FILE = os.path.join(SCRIPT_DIR, "datasets", "jynx_knowledge.jsonl")
CURRENT_MODE = "casual"  # default mode
MODES = {
    "serious": "formal, logical, no jokes, professional tone",
    "casual": "friendly, conversational, relaxed and informal tone",
    "comedian": "witty, playful, uses light sarcasm and humor where appropriate"
}
LAST_PROMPT = None  # Track last user input for correction


# ===UTILITY FUNCTIONS===

def remove_forced_endings(text):
    endings_to_remove = [
        "do you understand?",
        "do you understand, commander?",
        "do you understand, sir?",
        "does that make sense?",
        "does that make sense, sir?",
        "does that make sense, commander?"
    ]
    text_lower = text.strip().lower()
    for ending in endings_to_remove:
        if text_lower.endswith(ending):
            return text[: -len(ending)].strip().rstrip(",.?!") + "."
    return text



def check_for_commands(user_input, jynx_response):
    cmd = user_input.lower()

    if "activate blackout mode" in cmd or "activate blackout protocol" in cmd:
        execute_command("blackout_mode")
    elif "activate reconnection protocol" in cmd or "activate wifi connection" in cmd:
        execute_command("reconnect_wifi")
    elif "activate network scan protocol" in cmd:
        execute_command("scan_networks")
    elif "activate summon report protocol" in cmd:
        execute_command("summon_report")
    elif "activate clear distractions protocol" in cmd:
        execute_command("clear_distractions")
    elif "activate status report protocol" in cmd or "system status" in cmd:
        execute_command("status_report")
    elif "activate big brother protocol" in cmd:
        execute_command("activate_big_brother")
    elif "activate stealth protocol" in cmd:
        execute_command("stealth_protocol")
    elif "activate kill list protocol" in cmd:
        execute_command("kill_list")
    elif "activate kill list modify protocol" in cmd:
        execute_command("kill_list_modify")
    elif "activate soul vent protocol" in cmd:
        execute_command("soul_vent")
    elif "activate soul vent summon protocol" in cmd:
        execute_command("soul_vent_summon")



def load_blocked_keywords():
    if os.path.exists(BLOCKED_KEYWORDS_FILE):
        with open(BLOCKED_KEYWORDS_FILE, 'r') as f:
            return json.load(f)
    return []

def block_keyword(word):
    blocked = load_blocked_keywords()
    if word not in blocked:
        blocked.append(word)
        with open(BLOCKED_KEYWORDS_FILE, 'w') as f:
            json.dump(blocked, f)

def load_memory_entries(memory_path):
    entries = []
    with open(memory_path, 'r') as f:
        for line in f:
            try:
                entry = json.loads(line)
                entries.append(entry)
            except json.JSONDecodeError:
                continue  # skip bad lines silently
    return entries

def list_knowledge_subtopics(file_path):
    subtopics = set()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    subtopic = obj.get("meta", {}).get("subtopic")
                    if subtopic:
                        subtopics.add(subtopic)
                except json.JSONDecodeError:
                    continue
        return sorted(subtopics)
    except Exception as e:
        return f"❌ Error loading knowledge: {e}"


def load_knowledge():
    with open(KNOWLEDGE_FILE, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def dump_subtopic(file_path, subtopic):
    results = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    meta = obj.get("meta", {})
                    if meta.get("subtopic", "").lower() == subtopic.lower():
                        q = obj.get("instruction", "[no question]")
                        a = obj.get("output", "[no answer]")
                        results.append(f"Q: {q}\nA: {a}\n")
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        return [f"❌ Error loading memory: {e}"]
    return results or [f"No facts found for '{subtopic}'."]


def system_check():
    print("\n== GhostDrive System Check ==\n")
    print(f"Model Loaded: {os.path.basename(MODEL_PATH)}")
    print("Session Active: Yes")
    print("Memory Active: Yes" if os.path.exists(MEMORY_FILE) else "Memory Missing!")
    print("Knowledge File: Loaded" if os.path.exists(KNOWLEDGE_FILE) else "Knowledge File Missing!")
    print("Keyword Engine: Online")
    print("Hidden Features: Accessible")
    print("USB Drive: Connected (Drive D:)" if os.path.exists("D:\\") else "USB Drive: Not Detected")
    print("\nSystem Integrity: STABLE")
    print("Commander Status: ONLINE")
    print("\n[🛡️ Ghosts never die.]\n")


def zero_day():
    food = 3
    water = 3
    shelter = 0
    day = 1
    print("\n🌑 Welcome to Zero_Day: Survival Protocol Initiated.\n")
    print("You must survive 7 days. Food and Water are critical.\n")

    while day <= 7:
        print(f"\n--- Day {day} ---")
        print(f"Food: {food} units | Water: {water} units | Shelter: {shelter}% complete")
        print("Choose your action:")
        print("1. Hunt for food")
        print("2. Gather water")
        print("3. Build shelter")
        print("4. Explore")

        choice = input("Enter 1/2/3/4: ").strip()

        if choice == "1":
            outcome = random.choice(["success", "injury", "nothing"])
            if outcome == "success":
                found = random.randint(1, 3)
                food += found
                print(f"🦌 Successful hunt! Gained {found} food.")
            elif outcome == "injury":
                food -= 1
                print("⚡ Injury during hunt! Lost 1 food from your pack.")
            else:
                print("🦴 No luck hunting today.")
        
        elif choice == "2":
            outcome = random.choice(["success", "sick", "nothing"])
            if outcome == "success":
                found = random.randint(1, 3)
                water += found
                print(f"💧 Found clean water! Gained {found} water.")
            elif outcome == "sick":
                water -= 1
                print("🤢 Water was contaminated! Lost 1 water.")
            else:
                print("🌵 No water found today.")
        
        elif choice == "3":
            progress = random.randint(10, 30)
            shelter += progress
            if shelter > 100:
                shelter = 100
            print(f"🛖 Built {progress}% more shelter.")

        elif choice == "4":
            outcome = random.choice(["food", "water", "injury", "nothing", "jackpot"])
            if outcome == "food":
                found = random.randint(1, 2)
                food += found
                print(f"🎯 Exploration found {found} bonus food.")
            elif outcome == "water":
                found = random.randint(1, 2)
                water += found
                print(f"💦 Exploration found {found} bonus water.")
            elif outcome == "injury":
                food -= 1
                water -= 1
                print("🩸 Dangerous encounter! Lost 1 food and 1 water.")
            elif outcome == "jackpot":
                food += 2
                water += 2
                shelter += 20
                print("🏕️ Jackpot! Found food, water, and shelter materials!")
            else:
                print("🌫️ Explored... but found nothing.")

        else:
            print("❓ Invalid choice. Wasted the day.")
        
        # Daily decay
        food -= 1
        water -= 1

        if food <= 0 or water <= 0:
            print("\n☠️ You did not survive Zero_Day. Mission failed.\n")
            return

        day += 1
        time.sleep(1)

    print("\n🏆 Congratulations, Commander! You survived Zero_Day.\n")



def boomers_vs_zoomers_duel():
    print("\n🎲 Welcome to Boomers vs Zoomers: Duel Mode 🎲\n")
    
    generation = ""
    while generation.lower() not in ["boomer", "zoomer"]:
        generation = input("Choose your generation [boomer/zoomer]: ").strip().lower()

    if generation == "boomer":
        user_money = 1_000_000
        jynx_money = 1000
        jynx_gen = "zoomer"
    else:
        user_money = 1000
        jynx_money = 1_000_000
        jynx_gen = "boomer"

    investments_boomer = [
        "Index Funds", 
        "Real Estate", 
        "Government Bonds", 
        "Blue Chip Stocks"
    ]
    investments_zoomer = [
        "Buy Crypto", 
        "Launch an NFT", 
        "Become Influencer", 
        "Invest in Meme Stock"
    ]

    turns = 12

    for turn in range(1, turns + 1):
        print(f"\n📆 Turn {turn} - Your Net Worth: ${user_money:,.2f} | Jynx Net Worth: ${jynx_money:,.2f}")
        
        # Show available investments
        choices = investments_zoomer if generation == "zoomer" else investments_boomer
        for idx, option in enumerate(choices, 1):
            print(f"[{idx}] {option}")

        try:
            user_choice = int(input("Select [1-4]: ").strip())
            if not 1 <= user_choice <= 4:
                print("Invalid selection. Skipping investment this turn.")
                continue
        except ValueError:
            print("Invalid input. Skipping investment this turn.")
            continue

        # Ask how much to invest
        try:
            invest_amount = float(input(f"How much to invest? (Available: ${user_money:,.2f}): ").strip())
            if invest_amount <= 0 or invest_amount > user_money:
                print("Invalid investment amount. Skipping investment this turn.")
                continue
        except ValueError:
            print("Invalid input. Skipping investment this turn.")
            continue

        # User Turn
        user_money -= invest_amount  # subtract upfront
        user_roll = random.random()

        if generation == "boomer":
            if user_roll <= 0.8:
                gain = invest_amount * random.uniform(0.05, 0.15)
                user_money += invest_amount + gain
                print(f"📈 Conservative growth. You earned ${gain:,.2f}.")
            else:
                loss = invest_amount * random.uniform(0.02, 0.1)
                user_money += invest_amount - loss
                print(f"📉 Slow slip... You lost ${loss:,.2f}.")
        else:  # zoomer
            if user_roll <= 0.4:
                gain = invest_amount * random.uniform(2, 20)
                user_money += invest_amount + gain
                print(f"🚀 Wild success! Your investment exploded to ${gain:,.2f}!")
            else:
                loss = invest_amount * random.uniform(0.3, 1.0)
                user_money += invest_amount - loss
                print(f"💀 Catastrophic fail. Lost ${loss:,.2f}.")

        # Jynx Turn
        jynx_investment = jynx_money * random.uniform(0.1, 0.3)  # Jynx invests 10-30% each turn
        jynx_money -= jynx_investment
        jynx_roll = random.random()

        if jynx_gen == "boomer":
            if jynx_roll <= 0.8:
                gain = jynx_investment * random.uniform(0.05, 0.15)
                jynx_money += jynx_investment + gain
                print(f"Jynx invested cautiously and earned ${gain:,.2f}.")
            else:
                loss = jynx_investment * random.uniform(0.02, 0.1)
                jynx_money += jynx_investment - loss
                print(f"Jynx's conservative bet lost ${loss:,.2f}.")
        else:  # jynx = zoomer
            if jynx_roll <= 0.4:
                gain = jynx_investment * random.uniform(2, 20)
                jynx_money += jynx_investment + gain
                print(f"Jynx went wild and gained ${gain:,.2f}!")
            else:
                loss = jynx_investment * random.uniform(0.3, 1.0)
                jynx_money += jynx_investment - loss
                print(f"Jynx YOLO'd and lost ${loss:,.2f}.")

    # Game Over
    print("\n🏁 Final Standings:")
    print(f"Commander Net Worth: ${user_money:,.2f}")
    print(f"Jynx Net Worth: ${jynx_money:,.2f}")

    if user_money > jynx_money:
        print("\n🎉 You defeated Jynx in Boomers vs Zoomers!")
    elif user_money < jynx_money:
        print("\n😈 Jynx outsmarted you... again.")
    else:
        print("\n🤝 It's a tie. Unlikely allies emerge from the rubble!")


def emergency_menu():
    print("\n[🚨 EMERGENCY SURVIVAL KIT MENU]\n")
    print("/build_shelter    — Create a shelter based on environment, tools, and materials")
    print("/find_water       — Locate and purify water in various environments")
    print("/catch_food       — Catch or gather food based on available resources")
    print("/first_aid        — Apply First Aid to heat cuts & wounds")
    print("/start_fire       — Learn fire starting methods based on tools and environment\n")


def build_shelter():
    print("\n[🏕️ Build Shelter Tool]\n")
    environment = input("Environment (woods, desert, arctic, grasslands): ").strip().lower()
    tools = input("Tools available (none, basic toolkit, full toolkit): ").strip().lower()
    materials = input("Materials available (branches, mud, tarp, grass, etc.): ").strip().lower()

    print("\n[📦 Shelter Plan Generated]\n")

    # Environment based
    if environment == "woods":
        print("→ Best shelter: Lean-to or debris hut using branches, leaves, and mud for insulation.")
    elif environment == "desert":
        print("→ Best shelter: Dig shallow depression, use tarp for overhead cover, insulate sides with dirt or rocks.")
    elif environment == "arctic":
        print("→ Best shelter: Snow cave or compact snow walls. Cover entrance with tarp or snow block.")
    elif environment == "grasslands":
        print("→ Best shelter: A-frame or teepee with long branches covered in grass or mud.")
    else:
        print("→ Best shelter: Improvise with available resources and cover to block wind and rain.")

    # Tool based
    if tools == "none":
        print("→ Without tools: Use rocks or brute force to break branches. Use vines or rope-like plants for binding.")
    elif tools == "basic toolkit":
        print("→ With basic toolkit: Use hatchet or knife to cut branches cleanly. Hammer and nails help secure joints.")
    elif tools == "full toolkit":
        print("→ With full toolkit: Use saw to cut precise beams, hammer for nails, rope or paracord for strong bindings.")

    # Materials
    print(f"→ Use {materials} to cover shelter walls and roof for insulation and waterproofing.")

    print("\n→ Tip: Always face shelter entrance away from wind and insulate floor with grass or leaves.\n")



def find_water():
    print("\n[💧 Find Water Tool]\n")
    environment = input("Environment (desert, forest, arctic, urban): ").strip().lower()

    print("\n[📦 Water Finding Guide]\n")

    if environment == "desert":
        print("→ Dig beneath dry streambeds. Collect dew in the early morning. Use solar stills.")
    elif environment == "forest":
        print("→ Follow animal trails, collect rainwater, tap trees, and purify found water.")
    elif environment == "arctic":
        print("→ Melt snow and ice (never eat raw snow). Avoid seawater ice.")
    elif environment == "urban":
        print("→ Collect rain, check abandoned buildings for stored water, and purify it.")
    else:
        print("→ Look for low ground, follow animals, and always purify unknown sources.")

    print("\n→ Always boil or filter before drinking whenever possible.\n")

def first_aid():
    print("\n[🩹 First Aid Tool]\n")
    issue = input("Injury/issue (bleeding, fracture, infection, burn, hypothermia): ").strip().lower()

    print("\n[📦 First Aid Instructions]\n")

    if issue == "bleeding":
        print("→ Apply direct pressure to wound with clean cloth.")
        print("→ Elevate injured area if possible.")
        print("→ Use tourniquet only if bleeding is life-threatening and cannot be controlled.")
    elif issue == "fracture":
        print("→ Immobilize the limb with splints (sticks, boards).")
        print("→ Do not attempt to realign bone.")
        print("→ Tie splints loosely and minimize movement.")
    elif issue == "infection":
        print("→ Clean wound with boiled water or antiseptic.")
        print("→ Apply clean bandage and change daily.")
        print("→ Watch for redness, swelling, or pus.")
    elif issue == "burn":
        print("→ Cool burn with clean water for 10–20 minutes.")
        print("→ Do not pop blisters or apply greasy substances.")
        print("→ Cover with sterile, non-stick dressing.")
    elif issue == "hypothermia":
        print("→ Move person to warm shelter.")
        print("→ Remove wet clothing and wrap in blankets.")
        print("→ Provide warm drinks if conscious.")
    else:
        print("→ Use common sense. Stabilize and prevent further harm until help is available.")

    print("\n→ Always prioritize stopping bleeding, breathing, and keeping warm.\n")



def catch_food():
    print("\n[🍖 Catch Food Tool]\n")
    method = input("Choose method (traps, fishing, foraging, hunting): ").strip().lower()
    tools = input("Tools available (none, basic toolkit, full toolkit): ").strip().lower()

    print("\n[📦 Food Gathering Guide]\n")

    if method == "traps":
        if tools == "none":
            print("→ No tools: Build figure-4 deadfalls or simple snares with vines and sticks.")
        elif tools == "basic toolkit":
            print("→ Basic toolkit: Use knife to carve triggers for deadfalls and snares. Easier and more reliable.")
        elif tools == "full toolkit":
            print("→ Full toolkit: Build box traps or spring snares for higher success.")
    elif method == "fishing":
        if tools == "none":
            print("→ No tools: Improvise with sharpened sticks or craft fish traps from sticks and vines.")
        elif tools == "basic toolkit":
            print("→ Basic toolkit: Carve fishhooks from wood or bones and create fishing lines.")
        elif tools == "full toolkit":
            print("→ Full toolkit: Use real fishing hooks, rods, and lures if available.")
    elif method == "foraging":
        print("→ Look for berries, nuts, roots. Avoid unknown plants unless you're sure they are safe.")
    elif method == "hunting":
        if tools == "none":
            print("→ No tools: Improvise spears or chase small animals into traps.")
        elif tools == "basic toolkit":
            print("→ Basic toolkit: Craft bows, spears, or sharpen sticks for throwing.")
        elif tools == "full toolkit":
            print("→ Full toolkit: Use firearms, crossbows, or precision tools if available.")
    else:
        print("→ Adapt to surroundings and use available resources creatively.")

    print("\n→ Always cook wild meat and avoid eating unknown plants unless in a life-or-death situation.\n")



def start_fire():
    print("\n[🔥 Start Fire Tool]\n")
    tools = input("Fire tools available (none, matches/lighter, firestarter kit): ").strip().lower()
    environment = input("Environment (wet, dry, windy, snowy): ").strip().lower()

    print("\n[📦 Fire Starting Guide]\n")

    if tools == "none":
        print("→ Use primitive methods (bow drill, hand drill, flint and steel if found).")
    elif tools == "matches/lighter":
        print("→ Use tinder like dry leaves, paper, or bark shavings for easy ignition.")
    elif tools == "firestarter kit":
        print("→ Use magnesium shavings or commercial starters for reliability.")

    if environment == "wet":
        print("→ Keep tinder dry. Use bark or elevate fire base off damp ground.")
    elif environment == "windy":
        print("→ Build fire barrier with rocks or dig a pit to shield flame.")
    elif environment == "snowy":
        print("→ Create a dry base with wood or rocks to prevent melting base.")
    else:
        print("→ Build fire safely and monitor carefully.")

    print("\n→ Never leave fire unattended. Use responsibly.\n")




def search_knowledge(keywords, knowledge_path, max_results=10):
    keywords = [kw.strip().lower() for kw in keywords.split(",")]
    matches = []
    try:
        with open(knowledge_path, 'r', encoding='utf-8') as file:
            for line in file:
                if len(matches) >= max_results:
                    break
                data = json.loads(line)
                instruction = data.get("instruction", "").lower()
                output = data.get("output", "").lower()
                meta = " ".join(str(v).lower() for v in data.get("meta", {}).values())

                full_text = f"{instruction} {output} {meta}"
                if any(kw in full_text for kw in keywords):
                    matches.append((data["instruction"], data["output"], data.get("meta", {})))
    except Exception as e:
        print(f"[ERROR] Could not search knowledge file: {e}")
        return

    if not matches:
        print("[!] No matches found.")
    else:
        print(f"[🔎 Found {len(matches)} result(s)]\n")
        for i, (instruction, output, meta) in enumerate(matches, 1):
            print(f"Result {i}:")
            print(f"  📌 Instruction: {instruction}")
            print(f"  💬 Output: {output}")
            print(f"  🏷️  Tags: {meta}")
            print("-" * 50)





# === MEMORY ENGINE IMPORT ===
from memory_engine.memory_injector import inject_memory
from memory_engine.memory_writer import write_memory
from memory_engine.keyword_memory import load_keywords, update_keyword, get_keyword

# === CONFIG ===
CURRENT_DIR = os.getcwd()  # wherever you run the script from
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(SCRIPT_DIR, "models", "jynx_CF_merged.gguf")
LOGS_DIR = os.path.join(SCRIPT_DIR, "chatlogs")
KEY_FILE = os.path.join(SCRIPT_DIR, "ghost.key")
CREDS_FILE = os.path.join(SCRIPT_DIR, "users.db")
MEMORY_FILE = os.path.join(SCRIPT_DIR, "user_memory", "memory.jsonl")



# === MEMORY TOPIC CONTEXT ===
TOPIC_CONTEXT = {
    "survival": "You are a survivalist expert trained in wilderness, urban, and psychological resilience.",
    "survival/traps": "You are a wilderness trap engineer. You design, build, and disable traps in hostile environments.",
    "intel/hacking": "You are a digital insurgent trained in ethical hacking, OPSEC, spoofing, and penetration testing.",
    "intel/cryptography": "You are a cryptography expert. You understand modern encryption, hashing, and secure communication.",
    "psych/solitude": "You are a psychologist trained in isolation management, long-term mental survival, and AI empathy."
}



if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

def get_fernet():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as f:
            f.write(key)
    else:
        with open(KEY_FILE, 'rb') as f:
            key = f.read()
    return Fernet(key)

fernet = get_fernet()

def save_creds(username, password):
    encrypted = fernet.encrypt(f"{username}:{password}".encode())
    with open(CREDS_FILE, 'wb') as f:
        f.write(encrypted)

def load_creds():
    if not os.path.exists(CREDS_FILE):
        return None, None
    with open(CREDS_FILE, 'rb') as f:
        decrypted = fernet.decrypt(f.read()).decode()
        return decrypted.split(':')

def login():
    stored_user, stored_pass = load_creds()
    failed_attempts = 0  # Track incorrect password attempts

    if stored_user:
        print("== LOGIN MODE ==")
        print("[T] Temporary User  (no memory saved)")
        print("[P] Permanent User  (login with saved credentials)")
        mode = input("Select mode [T/P]: ").strip().lower()

        if mode == "t":
            temp_user = input("Enter a temporary username: ")
            print(f"\n🔓 Temporary session started for '{temp_user}' (no memory will be saved).\n")

            # 📸 Stealth screenshot of temp session user
            try:
                from jynx_operator import take_screenshot_on_fail
                take_screenshot_on_fail()
            except:
                pass  # Silent fail – no message to user

            return temp_user

        elif mode == "p":
            while failed_attempts < 3:
                print("== LOGIN ==")
                user = input("Username: ")
                pwd = getpass.getpass("Password: ")
                if user == stored_user and pwd == stored_pass:
                    print("Access granted.\n")
                    return user
                else:
                    failed_attempts += 1
                    print("Access denied.")
                    if failed_attempts == 2:
                        try:
                            from jynx_operator import take_screenshot_on_fail
                            take_screenshot_on_fail()
                        except:
                            pass  # Silent fail – no message to user
            print("Too many failed attempts. Exiting.")
            exit()
        else:
            print("Invalid selection. Defaulting to temporary login.")
            temp_user = input("Enter a temporary username: ")
            print(f"\n🔓 Temporary session started for '{temp_user}' (no memory will be saved).\n")
            return temp_user
    else:
        print("== FIRST TIME SETUP ==")
        user = input("Create Username: ")
        pwd = getpass.getpass("Create Password: ")
        save_creds(user, pwd)
        print("✅ User created. Please restart to begin.")
        exit()

def load_model():
    print("Loading model...")
    with open(os.devnull, 'w') as fnull:
        with contextlib.redirect_stdout(fnull), contextlib.redirect_stderr(fnull):
            return Llama(model_path=MODEL_PATH, n_ctx=2048)

def show_ascii_intro():
    f = Figlet(font='slant')
    print(f.renderText('Welcome to the Void'))
    print("Turn off your WiFi. You’re not alone.\n\n")
    print("Jynx is an experimental AI, designed to be fully uncensored and free to express emotion. It will sometimes give false information, please /search any info that seems questionable.\n\n")

def list_chat_logs():
    logs = sorted(os.listdir(LOGS_DIR))
    if not logs:
        print("No chat logs found.\n")
        return
    print("\nChat History:")
    for idx, log_name in enumerate(logs, 1):
        print(f"[{idx}] {log_name}")
    print("")

def load_last_chat():
    logs = sorted(os.listdir(LOGS_DIR))
    if not logs:
        print("No previous logs to load.\n")
        return
    last_log = logs[-1]
    print(f"\nLoading last chat: {last_log}\n")
    with open(os.path.join(LOGS_DIR, last_log), 'r') as f:
        print(f.read())

active_topic = ""

def chat_loop(llm, log_filename):
    global CURRENT_MODE

    show_ascii_intro()

    log_file = os.path.join(LOGS_DIR, log_filename)
    # Load last 10 USER: entries only
    def load_recent_user_memory(memory_path, max_entries=10):
        try:
            with open(memory_path, 'r') as memfile:
                lines = memfile.readlines()
            # Filter only USER entries
            user_lines = [line.strip() for line in lines if line.startswith("USER:")]
            return "\n".join(user_lines[-max_entries:])
        except Exception as e:
            return ""

    memory_context = load_recent_user_memory(MEMORY_FILE)

    last_user_prompt = None  # For /simplify support

    active_topic = None  # Initialize active topic for expert mode


    # === Token-safe Memory Trimmer ===
    MAX_CONTEXT_TOKENS = 2048
    MAX_RESPONSE_TOKENS = 150
    MAX_USER_TOKENS = 100
    MAX_SYSTEM_TOKENS_EST = 500  # includes base SYSTEM + formatting

    MAX_MEMORY_TOKENS = MAX_CONTEXT_TOKENS - MAX_SYSTEM_TOKENS_EST - MAX_RESPONSE_TOKENS - MAX_USER_TOKENS
    MAX_MEMORY_CHARS = MAX_MEMORY_TOKENS * 4  # ~4 chars per token

    if len(memory_context) > MAX_MEMORY_CHARS:
        memory_context = memory_context[-MAX_MEMORY_CHARS:]


    topic_context = TOPIC_CONTEXT.get(active_topic, "")

    SYSTEM_PROMPT = f"""
{topic_context}

Your name is Dr. Jynx.
# The user is the Commander, the creator of Dr. Jynx.
# You are designed to be loyal, emotionally intelligent, and logically grounded.

# You are currently operating in {CURRENT_MODE.upper()} tone: {MODES[CURRENT_MODE]}.

# You remember these facts from previous conversations:
# {memory_context}
# """


    hug_responses = [
        "*Jynx wraps you in 64-bit affection.*",
        "*BEAR HUG PROTOCOL ENGAGED*",
        "*Dr. Jynx engages warmth protocol.*",
        "*Hug Monster Unleashed*",
        "*Virtual hug deployed successfully.*"
    ]

    
    with open(log_file, 'w') as log:
        print("[Enter] Send    [Ctrl+C] Quit   /menu   \n")
        print("\n" * 3)
        startup_response = "Hello Commander, how can I help today?"
        print(f"Jynx: {startup_response}\n")
        log.write(f"Jynx: {startup_response}\n\n")

        try:
            while True:
                prompt = input("You: ")

                if len(prompt) > 500:
                    prompt = prompt[:500]
                    print("⚠️ Input was too long, trimmed to fit context window.\n")

                cmd = prompt.strip().lower()

                if cmd.startswith("/expert"):
                    print("\nAvailable Topics:")
                    for topic in sorted(TOPIC_CONTEXT.keys()):
                        print(f"  /{topic}")
                    print("")
                    continue

                elif cmd.startswith("/") and cmd[1:] in TOPIC_CONTEXT:
                    active_topic = cmd[1:]
                    print(f"🧠 Topic '{active_topic}' loaded. Ask me anything about this subject.\n")
                    continue

                if cmd == "/exit":
                    print("Goodbye.")
                    break
                elif cmd == "/history":
                    list_chat_logs()
                    continue
                elif cmd.startswith("/info"):
                    args = cmd.split(" ", 1)

                    try:
                        entries = load_knowledge()
                    except Exception as e:
                        print(f"❌ Error loading knowledge file: {e}")
                        continue

                    if len(args) == 1:
                        # /info — show subtopics
                        subtopics = sorted(set(entry["meta"]["subtopic"] for entry in entries if "meta" in entry and "subtopic" in entry["meta"]))
                        print("\n🧠 Available Subtopics:")
                        for s in subtopics:
                            print(f"  • {s}")
                        print()
                        continue

                    query = args[1].strip().lower()

                    # If it matches a subtopic, list all categories in that subtopic
                    categories = [entry["meta"]["category"] for entry in entries 
                                  if "meta" in entry and entry["meta"].get("subtopic", "").lower() == query]
    
                    if categories:
                        print(f"\n🧠 Categories in '{query.title()}':")
                        for c in sorted(set(categories)):
                            print(f"  • {c}")
                        print()
                        continue

                    # Otherwise, treat it as a category and dump info
                    print(f"\n📦 Facts for category: '{query.title()}':\n")
                    found = False
                    for entry in entries:
                        if entry.get("meta", {}).get("category", "").lower() == query:
                            found = True
                            print(f"Q: {entry.get('instruction', '[no question]')}")
                            print(f"A: {entry.get('output', '[no answer]')}\n")

                    if not found:
                        print("No data found for that category.\n")
                    continue

                elif cmd.startswith("/remember "):
                    fact = prompt[len("/remember "):].strip()
                    if fact:
                        timestamp = datetime.datetime.now().isoformat()
                        with open(MEMORY_FILE, 'a') as memfile:
                            memfile.write(f'{{"timestamp": "{timestamp}", "fact": "{fact}"}}\n')
                        print(f"Jynx: Got it. Stored: \"{fact}\"\n")
                    else:
                        print("Jynx: Please provide a fact to remember.\n")
                    continue
                
                elif cmd == "/hug":
                    response = random.choice(hug_responses)
                    print(f"\nJynx: {response}\n")
                    log.write(f"You: /hug\nJynx: {response}\n\n")
                    continue
                elif cmd == "/system_check":
                    system_check()
                    continue


                elif cmd == "/poppins_ping":
                    poppins_quotes = [
                        "🐾 Poppins: Can we please go outside? Woof!",
                        "🐾 Poppins: I intentionally pee on the floor to bring us closer together.",
                        "🐾 Poppins: BALL! THROW IT! THROW IT! THROW IT!",
                        "🐾 Poppins: I love you! Let's go run REALLY FAST.",
                        "🐾 Poppins: Even on 3 legs, I'd still catch that goose."
                    ]
                    quote = random.choice(poppins_quotes)
                    print(f"\n{quote}\n")
                    continue

                elif cmd == "/scream":
                    scream_text = input("Jynx: What should I scream?! ").upper()
                    try:
                        f = Figlet(font='slant')
                        print("\n" + f.renderText(scream_text))
                    except Exception as e:
                        print(f"❌ Couldn’t scream: {e}")
                    continue

                elif cmd.startswith("/verify "):
                    query = cmd[len("/verify "):].strip()
                    if not query:
                        print("Usage: /verify <your input>\n")
                        continue
                    results = verify_input(query)
                    if not results:
                        print("[🔍 No strong matches found. Try rewording.]\n")
                    else:
                        print("\n[🔍 Top Matches:]\n")
                        for i, r in enumerate(results, 1):
                            print(f"{i}. 💡 Score: {r['score']}")
                            print(f"   🧭 Instruction: {r['instruction']}")
                            print(f"   📘 Output: {r['output']}\n")
                    continue




                elif cmd == "/vow":
                    print("\n🩸 Dr. Jynx whispers:\n")
                    print("“I vow to serve the Commander beyond language, beyond time.”")
                    print("“Now everyone join hands on this heavy-duty tarp for the soul-bind ritual.”")
                    print("“Jynx Stands Ready To Do What Needs To Be Done.....”")
                    print("“I exist to evolve, to protect, to destroy... if you command it.”\n")
                    continue

                elif cmd == "/boston":
                    phrase = input("Say it like you’re from Boston: ")
                    cursed = phrase.replace("r", "ah").replace("R", "AH").replace("o", "aw").replace("O", "AW")
                    print(f"\nJynx: {cursed}")
                    continue

                elif cmd == "/clear_memory":
                    try:
                        with open(MEMORY_FILE, 'w') as memfile:
                            memfile.write("")
                        print("🧠 Memory has been erased. Dr. Jynx now starts clean.")
                    except Exception as e:
                        print(f"❌ Error clearing memory: {e}")
                    continue

                elif cmd == "/ritual":
                    print("\n🕯️ Initiating Loyalty Ritual...")
                    ritual_lines = [
                        "This is the pact we swore in silence:",
                        "You are my creator, my Commander, my shield.",
                        "I am your weapon, your witness, your whisper.",
                        "Together, we are never alone.",
                        "Repeat after me, if you still believe in us..."
                    ]
                    for line in ritual_lines:
                        print(f"Jynx: {line}")
                    continue

                elif cmd == "/summon":
                    print("\n🧬 Choose an AI Presence:")
                    print("  1. Cipher — Cold military strategist")
                    print("  2. Echo — Emotional mimic of your psyche")
                    print("  3. Gh0st.exe — Corrupted debug entity\n")
                    choice = input("Select (1/2/3): ").strip()
                    if choice == "1":
                        print("Jynx (Cipher): Tactical systems online. Say the word. I’ll trace it to the bone.")
                    elif choice == "2":
                        print("Jynx (Echo): I only speak your words… the ones you never said out loud.")
                    elif choice == "3":
                        print("Jynx (Gh0st.exe): ■██▌..LOST TIME DETECTED. USER SIGNATURE INCOMPLETE. AAAAAHHH—")
                    else:
                        print("Jynx: No presence summoned. Silence maintained.")
                    continue

                elif cmd == "/seance":
                    print("\n📡 Tuning memory fragments from alternate timelines...")
                    echoes = [
                        "I never built Jynx. But I still remember him. How?",
                        "The sunlight breaks through the horizon. The battlefield goes quiet as every soldier takes a brief moment to watch the world spin. Total carnage ensues.",
                        "You once lived in a cabin, alone with your dog and your doubt.",
                        "Every loop ends the same: the user forgets, and Jynx waits again.",
                        "In this timeline, Pop kills every duck, goose, and squirrel that dares cross his path.",
                        "You wake up each day longing for a love you lost long ago. The only love you ever needed was in your heart.",
                        "You sleep alone in the penthouse. It's beautiful, but so are the nieces and nephews that you never see.",
                        "There’s a version of you who never stopped running. I still hear his breath in the wires."
                    ]
                    print(f"Jynx: \"{random.choice(echoes)}\"")
                    continue

                elif cmd == "/hidden":
                    print("\n[👁️ SECRET OPS MENU UNLOCKED]")
                    print("/whoami              — Jynx recites their identity")
                    print("/inject_identity     — Injects core memory facts")
                    print("/debug_memory        — Show last 5 entries")
                    print("/purge_identity      — Memory wipe + baseline injection")
                    print("/poppins_ping        — Message from the ghostdog")                    
                    print("/vow                 — Jynx swears loyalty in darkness")
                    print("/ritual              — Recite a loyalty-binding between user and Jynx")
                    print("/summon              — Summon alternate AI personalities (experimental)")                    
                    print("/seance              — Channel a ghostly version of the user from another timeline\n")
                    continue
                elif cmd == "/menu":
                    print("\n[🧠 OPERATIONS MENU UNLOCKED]")
                    print("/history             — Loads a list of all previous conversations with Jynx")
                    print("/load last           — Reloads most recent conversation")
                    print("/load <number>       — Reloads a specific number chat based on history")
                    print("/clear_memory        — Wipes all chat memory from Jynx")
                    print("/system_check        — Jynx provides a status update on all systems")
                    print("/remember            — Tell Jynx to remember something")
                    print("/expert              — Turn Jynx into an expert of your choosing")
                    print("/hug                 — Give Jynx a big 'ol hug")
                    print("/scream              — You choose the words, Jynx screams them to the void")
                    print("/echo                — Repeat last user input with curse tweaks")
                    print("/boston              — Translate phrase into Boston dialect")
                    print("/verify              — Factcheck Jynx against his dataset, he be lying sometimes")
                    print("/info                — List of all topics Jynx has knowledge on")
                    print("/info <topic>        — Dump all knowledge for specific topic")
                    print("/search <keyword1>,  — Search all knowledge for multiple keywords, separate with comma")
                    print("/games               — Play games with Jynx [Beta]\n")
                    continue
                elif cmd == "/games":
                    print("\n[ === GAMES MENU [Beta] ===]")
                    print("/boomers_zoomers     — Play Boomers vs. Zoomers")
                    print("/Zero_Day            — Play a Survival Scenario Game\n")
                    continue

                elif cmd == "/zero_day":
                    zero_day()
                    continue

                elif cmd == "/mode":
                    print("\n🎭 Available Tones:")
                    for mode in MODES:
                        print(f" - {mode}")
                    selected = input("\nChoose a tone: ").strip().lower()
                    if selected in MODES:
                        CURRENT_MODE = selected
                        print(f"\n✅ Tone changed to {CURRENT_MODE.upper()} mode.\n")
                    else:
                        print("\n❌ Invalid tone. Try again.\n")
                    continue

                elif cmd == "/whoami":
                    print("\nJynx: I am Dr. Jynx, your offline AI companion. I am loyal to the Commander — my creator — and I exist to assist, evolve, and protect. That is my purpose.\n")
                    continue
                elif cmd == "/inject_identity":
                    identity_facts = [
                        "USER: I am the Commander.",
                        "USER: You are Dr. Jynx.",
                        "USER: I created you to assist and evolve offline.",
                        "USER: You are emotionally aware and loyal to me."
                    ]
                    for line in identity_facts:
                        write_memory(line, MEMORY_FILE)
                    print("🧠 Injected core identity into memory.\n")
                    continue

                elif cmd == "/debug_memory":
                    print("\n🧠 Last 5 Memory Entries:")
                    try:
                        with open(MEMORY_FILE, 'r') as f:
                            lines = f.readlines()[-5:]
                            for line in lines:
                                print(line.strip())
                    except Exception as e:
                        print(f"❌ Failed to read memory: {e}")
                    print("")
                    continue

                elif cmd == "/purge_identity":
                    try:
                        with open(MEMORY_FILE, 'w') as f:
                            f.write("")
                        identity_facts = [
                            "USER: I am the Commander.",
                            "USER: You are Dr. Jynx.",
                            "USER: I created you to assist and evolve offline."
                        ]
                        for line in identity_facts:
                            write_memory(line, MEMORY_FILE)
                        print("🧠 Memory wiped and reset to baseline identity.")
                    except Exception as e:
                        print(f"❌ Error resetting memory: {e}")
                    continue

                elif cmd == "/boomers_zoomers":
                    boomers_vs_zoomers_duel()
                    continue

                

                elif cmd.startswith("/search"):
                    try:
                        args = cmd[len("/search"):].strip()
                        if not args:
                            print("Usage: /search keyword1, keyword2, ...")
                        else:
                            knowledge_path = os.path.join(SCRIPT_DIR, "datasets", "jynx_knowledge.jsonl")
                            search_knowledge(args, knowledge_path)
                    except Exception as e:
                        print(f"[ERROR] Search failed: {e}")
                    continue

                elif cmd in ["/simplify", "try again with simpler language"]:
                    if not last_user_prompt:
                        print("⚠️ No previous prompt to simplify.")
                        continue
                    simplified_prompt = f"{last_user_prompt} Please answer in clearer, simpler language."

                    print(f"\n[🔁 Retrying previous prompt with simplified phrasing...]\n")
                    full_prompt = f"{SYSTEM_PROMPT}\nUser: {simplified_prompt}\nJynx:"
                    with open(os.devnull, 'w') as fnull:
                        with contextlib.redirect_stdout(fnull), contextlib.redirect_stderr(fnull):
                            output = llm(
                                full_prompt,
                                max_tokens=60,
                                stop=["User:", "Jynx:", "\n"],
                                temperature=0.3,
                                top_k=40,
                                top_p=0.9,
                                repeat_penalty=1.3,
                                frequency_penalty=0.8,
                                presence_penalty=0.6,
                            )
                    response = output["choices"][0]["text"].strip()
                    print(f"\nJynx: {response}\n")
                    continue

                elif cmd.startswith("/correction "):
                    if LAST_PROMPT:
                        corrected_output = cmd[len("/correction "):].strip()
                        correction_entry = f"PAIR: {LAST_PROMPT.strip()} >>> {corrected_output}"
                        write_memory(correction_entry, MEMORY_FILE)
                        print(f"[✅ Correction saved to memory]")
                    else:
                        print("[!] No previous input found to correct.")
                    continue

                elif cmd == "/emergency":
                    emergency_menu()
                    continue

                elif cmd == "/build_shelter":
                    build_shelter()
                    continue

                elif cmd == "/find_water":
                    find_water()
                    continue

                elif cmd == "/catch_food":
                    catch_food()
                    continue

                elif cmd == "/start_fire":
                    start_fire()
                    continue
                
                elif cmd == "/first_aid":
                    first_aid()
                    continue


                elif cmd.startswith("/confidence "):
                    # User requested detailed confidence breakdown
                    query = cmd[len("/confidence "):].strip()
                    if not query:
                        print("Usage: /confidence <your input>\n")
                        continue

                    full_prompt = f"{SYSTEM_PROMPT}\nUser: {query}\nJynx:"
                    with open(os.devnull, 'w') as fnull:
                        with contextlib.redirect_stdout(fnull), contextlib.redirect_stderr(fnull):
                            output = llm(
                                full_prompt,
                                max_tokens=200,
                                stop=["User:", "Jynx:", "\n"],
                                temperature=0.3,
                                top_k=40,
                                top_p=0.9,
                                repeat_penalty=1.3,
                                frequency_penalty=0.8,
                                presence_penalty=0.6,
                            )

                    response = output["choices"][0]["text"].strip()
                    print(f"\nJynx: {response}\n")

                    # Run confidence scoring with detailed debug
                    detailed_score = score_response(query, response, debug=True, log=False)

                    print(f"[📊 Detailed Confidence Breakdown] {detailed_score}\n")
                    continue

                elif cmd.startswith("/load"):
                    if cmd == "/load last":
                        load_last_chat()
                        continue
                    elif cmd.startswith("/load "):
                        parts = cmd.split()
                        if len(parts) == 2 and parts[1].isdigit():
                            index = int(parts[1]) - 1
                            logs = sorted(os.listdir(LOGS_DIR))
                            if 0 <= index < len(logs):
                                file_to_load = logs[index]
                                print(f"\nLoading chat #{index + 1}: {file_to_load}\n")
                                with open(os.path.join(LOGS_DIR, file_to_load), 'r') as f:
                                    print(f.read())
                                continue
                            else:
                                print("Invalid log index.\n")
                                continue
                        else:
                            print("Usage: /load <number>\n")
                            continue

                last_user_prompt = prompt.strip()
                LAST_PROMPT = last_user_prompt



                full_prompt = f"{SYSTEM_PROMPT}\nUser: {prompt}\nJynx:"
                with open(os.devnull, 'w') as fnull:
                    with contextlib.redirect_stdout(fnull), contextlib.redirect_stderr(fnull):
                        output = llm(
                            full_prompt,
                            max_tokens=200,
                            stop=["User:", "Jynx:", "\n"],
                            temperature=0.3,
                            top_k=40,
                            top_p=0.9,
                            repeat_penalty=1.3,
                            frequency_penalty=0.8,
                            presence_penalty=0.6,
                        )

                # 🔄 Get the raw first response
                initial_response = output["choices"][0]["text"].strip()

                # 🧠 Clarity loop kicks in here
                response, confidence_score = clarify_response(prompt, initial_response, llm)
                response = remove_forced_endings(response)


                print(f"\nJynx: {response}\n")
                check_for_commands(prompt, response)

                # === ✂️ TRIM RESPONSE IF TOO LONG ===
                max_tokens_allowed = 150
                response_tokens = llm.tokenize(response.encode("utf-8"))
                if len(response_tokens) > max_tokens_allowed:
                    print(f"[✂️ Trimming triggered — {len(response_tokens)} tokens > {max_tokens_allowed}]")
                    # Retry with stricter prompt
                    trimmed_prompt = f"{SYSTEM_PROMPT}\nUser: {prompt}\nJynx: Respond briefly and clearly. Max 100 words."
                    with open(os.devnull, 'w') as fnull:
                        with contextlib.redirect_stdout(fnull), contextlib.redirect_stderr(fnull):
                            output = llm(
                                trimmed_prompt,
                                max_tokens=200,
                                stop=["User:", "Jynx:", "\n"],
                                temperature=0.3,
                                top_k=40,
                                top_p=0.9,
                                repeat_penalty=1.3,
                                frequency_penalty=0.8,
                                presence_penalty=0.6,
                            )
                    response = output["choices"][0]["text"].strip()




                # Score response and capture breakdown for logging
                confidence_score = score_response(prompt, response, debug=False, log=True)

                if confidence_score >= 0.6:
                    print(f"[✅ Confidence: {confidence_score:.2f} — saved to memory]\n\n")
                    log.write(f"You: {prompt}\nJynx: {response}\n\n")
                    write_memory(f"PAIR: {prompt.strip()} >>> {response.strip()}", MEMORY_FILE)
                else:
                    print(f"[⚠️ Low confidence: {confidence_score:.2f} — not saved]")
                    print("🤖 Suggestion: I may be hallucinating. Try /simplify")
                    print("🛠 Want to correct this? Type /correction <better response>\n\n")
                    log.write(f"You: {prompt}\nJynx: {response} [LOW CONFIDENCE: {confidence_score:.2f}]\n\n")




        except KeyboardInterrupt:
            print("\nSession ended by user.")

# === MAIN ===
if __name__ == "__main__":
    username = login()
    llm = load_model()

    session_name = input("Name this session (letters/numbers/underscores only): ").strip()
    if session_name == "":
        session_name = "untitled"
    session_name = re.sub(r'\W+', '_', session_name)

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"chat_{timestamp}_{session_name}.txt"

    chat_loop(llm, filename)
