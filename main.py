import flet as ft
from datetime import datetime
import requests
import threading
import time
import random
import json
import os

# --- Configuration ---
WEATHER_API_KEY = "d37bdb9d6df67051dff6c2dfd3ee6e42"
DATA_FILE = "smart_assistant_data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"name": None, "city": "Singapore", "tasks": []}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"name": None, "city": "Singapore", "tasks": []}

def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"Saved: {data}")  # debug
    except Exception as e:
        print(f"Error saving: {e}")

def get_weather(city):
    if not city:
        return "🌍 Please set your city"
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

def main(page: ft.Page):
    page.title = "Smart Daily Assistant"
    page.padding = 20
    page.bgcolor = ft.Colors.GREY_100
    page.window_width = 400
    page.window_height = 750
    page.scroll = ft.ScrollMode.AUTO

    # Load data
    data = load_data()
    stored_name = data.get("name")
    stored_city = data.get("city", "Singapore")
    tasks_list_data = data.get("tasks", [])  # list of dicts: {"text": str, "completed": bool}

    # --- Welcome Screen ---
    name_input = ft.TextField(hint_text="Enter your name", width=280, bgcolor=ft.Colors.WHITE, border_radius=30, text_align=ft.TextAlign.CENTER)
    city_input_on_welcome = ft.TextField(hint_text="Your city (for weather)", width=280, bgcolor=ft.Colors.WHITE, border_radius=30, text_align=ft.TextAlign.CENTER, value=stored_city)
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
            refresh_tasks_ui()  # load tasks from data

    # Gradient background
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

    # --- Main interface ---
    time_text = ft.Text("", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
    date_text = ft.Text("", size=16, color=ft.Colors.GREY_800)
    quotes = ["✨ Stay focused!", "💪 You are capable!", "🌟 Every day is new!", "🎯 Small steps!", "🔥 Believe!", "🌱 Your future self will thank you!"]
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

    # --- Task management using list and rebuild UI ---
    task_entries = []  # list of {"text": str, "completed": bool}
    tasks_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
    task_count_text = ft.Text("0 tasks", size=14, color=ft.Colors.GREY_700)

    def save_tasks_to_file():
        data["tasks"] = task_entries
        save_data(data)

    def refresh_tasks_ui():
        # Rebuild tasks_column from task_entries
        tasks_column.controls.clear()
        for idx, task in enumerate(task_entries):
            checkbox = ft.Checkbox(value=task["completed"], check_color=ft.Colors.BLUE_700)
            task_label = ft.Text(task["text"], size=16, expand=True)
            if task["completed"]:
                task_label.style = ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH, color=ft.Colors.GREY_500)

            delete_btn = ft.TextButton("🗑️", style=ft.ButtonStyle(color=ft.Colors.RED_400))

            def make_delete_callback(index):
                return lambda e: delete_task(index)
            delete_btn.on_click = make_delete_callback(idx)

            def make_toggle_callback(index):
                return lambda e: toggle_task_complete(index, checkbox)
            checkbox.on_change = make_toggle_callback(idx)

            row = ft.Container(
                content=ft.Row([checkbox, task_label, delete_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor=ft.Colors.WHITE,
                padding=10,
                border_radius=12,
            )
            tasks_column.controls.append(row)
        update_task_count()
        page.update()

    def update_task_count():
        count = len(task_entries)
        task_count_text.value = f"{count} task{'s' if count != 1 else ''}"

    def delete_task(index):
        del task_entries[index]
        save_tasks_to_file()
        refresh_tasks_ui()

    def toggle_task_complete(index, checkbox):
        task_entries[index]["completed"] = checkbox.value
        save_tasks_to_file()
        refresh_tasks_ui()  # refresh to show strikethrough

    def add_task_to_list(text):
        task_entries.append({"text": text, "completed": False})
        save_tasks_to_file()
        refresh_tasks_ui()

    task_input = ft.TextField(hint_text="What needs to be done?", width=250, height=45, bgcolor=ft.Colors.WHITE, border_radius=25, border_color=ft.Colors.BLUE_400, text_size=15)

    def add_task_clicked(e):
        if task_input.value:
            add_task_to_list(task_input.value)
            task_input.value = ""
            page.update()

    def clear_all_tasks(e):
        task_entries.clear()
        save_tasks_to_file()
        refresh_tasks_ui()

    # --- Weather ---
    weather_text = ft.Text("Loading...", size=15, color=ft.Colors.GREY_800)
    def update_weather():
        city = data.get("city", "Singapore")
        weather_text.value = get_weather(city)
        page.update()

    # --- Main layout ---
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
        ft.Row([ft.Text("📋 My Tasks", size=20, weight=ft.FontWeight.BOLD), task_count_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Row([task_input, ft.TextButton("➕ Add", on_click=add_task_clicked, style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=25)))]),
        ft.Row([ft.TextButton("🗑️ Clear all", on_click=clear_all_tasks, style=ft.ButtonStyle(color=ft.Colors.RED_600))], alignment=ft.MainAxisAlignment.END),
        ft.Container(content=tasks_column, height=280, bgcolor=ft.Colors.GREY_100, border_radius=15, padding=10),
        ft.Container(
            content=ft.Column([
                ft.Row([ft.Text("☁️", size=20), ft.Text("Weather Advice", size=16, weight=ft.FontWeight.BOLD)]),
                weather_text,
                ft.TextButton("Refresh", on_click=lambda e: update_weather(), style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_500, color=ft.Colors.WHITE)),
            ], spacing=8),
            bgcolor=ft.Colors.ORANGE_100,
            padding=15,
            border_radius=15,
        ),
    ], scroll=ft.ScrollMode.AUTO, expand=True)

    # Initialization for returning user
    if stored_name:
        greeting_name.value = f"Hello {stored_name}! 👋"
        start_time_updates()
        update_weather()
        start_motivation_rotation()
        # Load tasks from stored list
        task_entries.clear()
        task_entries.extend(tasks_list_data)
        refresh_tasks_ui()
        quote_text.value = random.choice(quotes)

    page.add(welcome_container, main_container)

if __name__ == "__main__":
    ft.app(target=main)