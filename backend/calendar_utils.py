import json
import os

CALENDAR_FILE = os.path.join("backend/static_data", "calendar_events.json")


def add_calendar_event(title: str, date: str):
    """Add a new event to the calendar JSON file, avoiding duplicate entries."""
    os.makedirs("backend/static_data", exist_ok=True)
    events = []
    if os.path.exists(CALENDAR_FILE):
        try:
            with open(CALENDAR_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    events = json.loads(content)
                else:
                    print("📝 Calendar file exists but is empty, starting fresh")
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing error in calendar file: {e}")
            print("📝 Starting with empty events list")
            events = []
        except Exception as e:
            print(f"⚠️ Error reading calendar file: {e}")
            events = []
    else:
        print("📝 No existing events file found, starting fresh")

    if any(e.get("title") == title and e.get("date") == date for e in events):
        print(f"⚠️ Event already exists: {title} on {date}")
        return

    events.append({"title": title, "date": date})

    try:
        with open(CALENDAR_FILE, "w", encoding="utf-8") as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        print(f"✅ Successfully saved {len(events)} events to {CALENDAR_FILE}")
    except Exception as e:
        print(f"❌ Failed to save calendar events: {e}")
