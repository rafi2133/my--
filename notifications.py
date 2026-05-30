import json
import os

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def save_notification(title, desc, start, end):
    notifications = load_notifications()
    notifications.append({
        "title": title,
        "description": desc,
        "start": start,
        "end": end
    })
    with open(f"{DATA_DIR}/notifications.json", "w") as f:
        json.dump(notifications, f)

def load_notifications():
    try:
        with open(f"{DATA_DIR}/notifications.json", "r") as f:
            return json.load(f)
    except:
        return []