===========================================================
               GHOSTDRIVE 2.0 - COMMANDS & PROTOCOLS
===========================================================

This document outlines the built-in commands and protocols supported by GhostDrive’s offline CLI system (ghostcli.py and jynx_operator.py). These are typed directly into the terminal interface.

===========================================================
CORE PROTOCOLS (Jynx Operator Level)
===========================================================

These are invoked via chat commands like “activate blackout protocol” or directly from the CLI:

🔌 activate blackout protocol
→ Disconnects WiFi + mutes system volume (offline stealth mode)

🕶️ activate stealth protocol
→ Mutes audio, enables dark mode, and activates power saving (Windows only)

🌐 activate network scan protocol
→ Lists nearby WiFi networks

📡 activate reconnection protocol
→ Reconnects to predefined WiFi

🧠 activate summon report protocol
→ Shows Jynx usage stats: days active, sessions, and total messages

🧼 activate clear distractions protocol
→ Closes distracting apps like Chrome/Spotify + clears clipboard (Windows only)

📋 activate status report protocol
→ Shows system uptime, battery level, IP address, and active user

👁️ activate big brother protocol
→ Opens OpenAI ChatGPT in the default browser

📓 activate soul vent protocol
→ Opens a journal entry with a random reflection prompt

📂 activate soul vent summon protocol
→ Lists past journal entries and lets user reopen any of them

🗡️ activate kill list protocol
→ Displays a saved TO-DO list of tasks from kill_list.txt

🩸 activate kill list modify protocol
→ Add/remove tasks to/from the TO-DO list interactively

===========================================================
TERMINAL COMMANDS (GhostCLI Shortcuts)
===========================================================

These are typed directly in the chat with a `/` prefix:

📁 /menu  
→ Show full list of available operational commands

🧠 /info or /info <topic>
→ Lists topics or dumps data from Jynx’s structured memory

🔍 /search keyword1, keyword2
→ Searches Jynx’s internal dataset for facts matching the keywords

💬 /remember <fact>
→ Saves a fact to Jynx’s long-term memory file

🧹 /clear_memory
→ Erases all long-term memory data

🛠 /system_check
→ Runs diagnostic: model, logs, drive detection, and memory health

😈 /ritual or /vow
→ Loyalty sequences (text-based interactions with Jynx)

🧬 /summon or /seance
→ Summon alternate AI personalities or memory echoes

🐾 /poppins_ping
→ Generates a random dog quote from Pop (the ghostdog)

🎭 /mode
→ Switch Jynx’s personality tone (casual, serious, comedian)

🔥 /scream
→ Enter a phrase and Jynx will shout it in giant ASCII letters

🎲 /games
→ Opens mini-games menu (Boomers vs. Zoomers, Zero_Day survival)

===========================================================
SURVIVAL TOOLS (CLI MINI MODULES)
===========================================================

Use these commands to simulate offline emergency scenarios:

/build_shelter      → Generates shelter plans based on conditions  
/find_water         → Teaches how to locate/purify water  
/catch_food         → Teaches food gathering: traps, foraging, hunting  
/start_fire         → Provides fire-starting guidance  
/first_aid          → Gives medical tips for wounds, hypothermia, etc.  

===========================================================

All protocols are processed entirely offline. GhostDrive does not require or use an internet connection.

Project Lead: Ryan Himes  
System: GhostDrive 2.0  
Model: Jynx (quantized GGUF)  
License: CC BY-NC 4.0  
