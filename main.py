import flet as ft
from datetime import datetime
import requests
import threading
import time
import random
import json
import os

# --- Configuration ---
DATA_FILE = "smart_assistant_data.json"
WEATHER_API_KEY = "d37bdb9d6df67051dff6c2dfd3ee6e42"

# --- Helper Functions ---
def load_data():
    """Load user data from JSON file."""
    if not os.path.exists(DATA_FILE):
        return {"name": None, "city": "Singapore", "tasks": []}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"name": None, "city": "Singapore", "tasks": []}

def save_data(data):
    """Save user data to JSON file."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def get_weather(city):
    """Fetch weather from API."""
    if not city:
        return "🌍 Please set your city in settings"
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=10)
        data = response.json()
        temp = data['main']['temp']
        if temp > 25:
            advice = "🥵 Wear light clothes! It's hot."
        elif temp < 15:
            advice = "🧥 Wear a jacket! It's cool."
        else:
            advice = "✅ Enjoy your day!"
        return f"{temp:.1f}°C | {advice}"
    except:
        return "⚠️ Could not fetch weather. Check city name."

# --- Main App ---
def main(page: ft.Page):
    page.title = "Smart Daily Assistant"
    page.padding = 20
    page.bgcolor = ft.Colors.GREY_100
    page.window_width = 400
    page.window_height = 750
    page.scroll = ft.ScrollMode.AUTO

    # Load persistent data
    data = load_data()
    stored_name = data.get("name")
    stored_city = data.get("city", "Singapore")
    stored_tasks = data.get("tasks", [])

    # --- Welcome Screen (only if no name saved) ---
    name_input = ft.TextField(
        hint_text="Enter your name",
        width=280,
        bgcolor=ft.Colors.WHITE,
        border_radius=30,
        text_align=ft.TextAlign.CENTER,
    )
    city_input_on_welcome = ft.TextField(
        hint_text="Your city (for weather)",
        width=280,
        bgcolor=ft.Colors.WHITE,
        border_radius=30,
        text_align=ft.TextAlign.CENTER,
        value=stored_city
    )
    greeting_name = ft.Text("", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
    welcome_container = ft.Container(visible=stored_name is None, expand=True)
    main_container = ft.Container(visible=stored_name is not None, expand=True)

    def save_name_and_city(e):
        if name_input.value and city_input_on_welcome.value:
            data["name"] = name_input.value
            data["city"] = city_input_on_welcome.value
            save_data(data)
            greeting_name.value = f"Hello {name_input.value}! 👋"
            welcome_container.visible = False
            main_container.visible = True
            page.update()
            start_time_updates()
            update_weather()
            start_motivation_rotation()
            load_tasks()

    # Gradient welcome screen
    welcome_container.content = ft.Container(
        gradient=ft.LinearGradient(colors=["#DB5C40", "#BB62DE", "#DE62D0", "#D9093F"]),
        expand=True,
        content=ft.Column([
            ft.Container(height=60),
            ft.Text("🌤️", size=90),
            ft.Text("Smart Assistant", size=34, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Text("Your Daily Companion", size=16, color=ft.Colors.WHITE70),
            ft.Container(height=20),
            ft.Text("Keep yourself on the track!", size=18, weight=ft.FontWeight.W_500, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
            ft.Container(height=30),
            name_input,
            ft.Container(height=10),
            city_input_on_welcome,
            ft.Container(height=20),
            ft.FilledButton("Get Started", on_click=save_name_and_city, width=220, height=50,
                            style=ft.ButtonStyle(bgcolor=ft.Colors.WHITE, color="#DB5C40", shape=ft.RoundedRectangleBorder(radius=30))),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
    )

    # --- Main App Interface ---
    time_text = ft.Text("", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
    date_text = ft.Text("", size=16, color=ft.Colors.GREY_800)
    quotes = [
        "✨ Stay focused and never give up!",
        "💪 You are capable of amazing things!",
        "🌟 Every day is a new opportunity!",
        "🎯 Small steps lead to big results!",
        "🔥 Believe in yourself!",
        "🌱 Your future self will thank you!"
    ]
    quote_text = ft.Text(random.choice(quotes), size=13, italic=True, color=ft.Colors.GREY_700, text_align=ft.TextAlign.CENTER)

    def update_quote():
        while True:
            time.sleep(30)
            quote_text.value = random.choice(quotes)
            page.update()

    def start_motivation_rotation():
        threading.Thread(target=update_quote, daemon=True).start()

    def update_time():
        while True:
            now = datetime.now()
            time_text.value = now.strftime("%I:%M:%S %p")
            date_text.value = now.strftime("%A, %B %d, %Y")
            page.update()
            time.sleep(1)

    def start_time_updates():
        threading.Thread(target=update_time, daemon=True).start()

    # --- Task Management ---
    tasks_list = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
    task_count_text = ft.Text("0 tasks", size=14, color=ft.Colors.GREY_700)

    def update_task_count():
        count = len(tasks_list.controls)
        task_count_text.value = f"{count} task{'s' if count != 1 else ''}"
        # Save tasks to JSON
        tasks_data = []
        for task_container in tasks_list.controls:
            checkbox = task_container.content.controls[0]
            task_text = task_container.content.controls[1]
            tasks_data.append({"text": task_text.value, "completed": checkbox.value})
        data["tasks"] = tasks_data
        save_data(data)

    def load_tasks():
        tasks_list.controls.clear()
        for task in stored_tasks:
            add_task_from_data(task["text"], task["completed"])
        update_task_count()

    def add_task_from_data(task_text_value, completed=False):
        checkbox = ft.Checkbox(value=completed, check_color=ft.Colors.BLUE_700)
        task_label = ft.Text(task_text_value, size=16, expand=True)
        if completed:
            task_label.style = ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH, color=ft.Colors.GREY_500)
        delete_btn = ft.TextButton("🗑️", style=ft.ButtonStyle(color=ft.Colors.RED_400))

        row = ft.Container(
            content=ft.Row([checkbox, task_label, delete_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor=ft.Colors.WHITE,
            padding=10,
            border_radius=12,
        )

        def delete_clicked(e):
            tasks_list.controls.remove(row)
            update_task_count()
            page.update()

        delete_btn.on_click = delete_clicked

        def toggle_complete(e):
            if checkbox.value:
                task_label.style = ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH, color=ft.Colors.GREY_500)
            else:
                task_label.style = ft.TextStyle(decoration=None, color=ft.Colors.BLACK)
            update_task_count()
            page.update()

        checkbox.on_change = toggle_complete

        tasks_list.controls.append(row)
        page.update()

    task_title = ft.TextField(
        hint_text="What needs to be done?",
        width=250,
        height=45,
        bgcolor=ft.Colors.WHITE,
        border_radius=25,
        border_color=ft.Colors.BLUE_400,
        text_size=15,
    )

    def add_task(e):
        if task_title.value:
            add_task_from_data(task_title.value, False)
            task_title.value = ""
            page.update()

    def clear_all(e):
        tasks_list.controls.clear()
        update_task_count()
        page.update()

    # --- Weather Section ---
    weather_text = ft.Text("Loading...", size=15, color=ft.Colors.GREY_800)

    def update_weather():
        city = data.get("city", "Singapore")
        weather_text.value = get_weather(city)
        page.update()

    # --- Main Layout (Responsive, no Settings button) ---
    main_container.content = ft.Column([
        ft.Container(
            content=ft.Column([
                ft.Row([ft.Text("🌤️", size=36), greeting_name], alignment=ft.MainAxisAlignment.CENTER),
                time_text,
                date_text,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                quote_text,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.Colors.BLUE_50,
            padding=20,
            border_radius=15,
        ),
        ft.Row([ft.Text("📋 My Tasks", size=20, weight=ft.FontWeight.BOLD), task_count_text],
               alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Row([task_title, ft.TextButton("➕ Add", on_click=add_task,
                                         style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=25)))]),
        ft.Row([ft.TextButton("🗑️ Clear all", on_click=clear_all, style=ft.ButtonStyle(color=ft.Colors.RED_600))],
               alignment=ft.MainAxisAlignment.END),
        ft.Container(content=tasks_list, height=280, bgcolor=ft.Colors.GREY_100, border_radius=15, padding=10),
        ft.Container(
            content=ft.Column([
                ft.Row([ft.Text("☁️", size=20), ft.Text("Weather Advice", size=16, weight=ft.FontWeight.BOLD)]),
                weather_text,
                ft.TextButton("Refresh", on_click=lambda e: update_weather(),
                             style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_500, color=ft.Colors.WHITE)),
            ], spacing=8),
            bgcolor=ft.Colors.ORANGE_100,
            padding=15,
            border_radius=15,
        ),
    ], scroll=ft.ScrollMode.AUTO, expand=True)

    # Initialize for returning users
    if stored_name:
        greeting_name.value = f"Hello {stored_name}! 👋"
        start_time_updates()
        update_weather()
        start_motivation_rotation()
        load_tasks()
        quote_text.value = random.choice(quotes)

    page.add(welcome_container, main_container)

if __name__ == "__main__":
    ft.app(target=main)