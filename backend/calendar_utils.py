# calendar_utils.py

import os
import json

CALENDAR_FILE = os.path.join("static_data", "calendar_events.json")

def add_calendar_event(title: str, date: str):
    os.makedirs("data", exist_ok=True)
    if os.path.exists(CALENDAR_FILE):
        with open(CALENDAR_FILE, "r", encoding="utf-8") as f:
            events = json.load(f)
    else:
        events = []

    # Prevent duplicates
    if any(e["title"] == title and e["date"] == date for e in events):
        return

    events.append({ "title": title, "date": date })
    with open(CALENDAR_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2)
