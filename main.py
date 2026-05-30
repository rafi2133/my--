import flet as ft
from datetime import datetime
import requests
import threading
import time
import random

# Weather API
WEATHER_API_KEY = "d37bdb9d6df67051dff6c2dfd3ee6e42"
CITY = "Singapore"

# Motivational quotes
QUOTES = [
    "✨ Stay focused and never give up!",
    "💪 You are capable of amazing things!",
    "🌟 Every day is a new opportunity!",
    "🎯 Small steps lead to big results!",
    "🔥 Believe in yourself!",
    "🌱 Your future self will thank you!",
]

def get_weather():
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric"
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
        return "28°C | ☀️ Wear something light!"

def main(page: ft.Page):
    page.title = "Smart Daily Assistant"
    page.padding = 20
    page.bgcolor = ft.Colors.GREY_100
    page.window_width = 400
    page.window_height = 750
    page.scroll = ft.ScrollMode.AUTO

    # ========== IMPROVED WELCOME SCREEN ==========
    name_input = ft.TextField(
        hint_text="Enter your name",
        width=280,
        bgcolor=ft.Colors.WHITE,
        border_radius=30,
        text_size=16,
        text_align=ft.TextAlign.CENTER,
    )
    
    greeting_name = ft.Text("", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
    welcome_container = ft.Container(visible=True, expand=True)
    main_container = ft.Container(visible=False, expand=True)

    def start_app(e):
        if name_input.value:
            greeting_name.value = f"Hello {name_input.value}! 👋"
            welcome_container.visible = False
            main_container.visible = True
            page.update()
            start_time_updates()
            update_weather()
            start_motivation_rotation()

    # Beautiful gradient background (simple, no compatibility issues)
    welcome_container.content = ft.Container(
        gradient=ft.LinearGradient(
            colors=["#DB5C40", "#BB62DE", "#DE62D0", "#D9093F"],
        ),
        expand=True,
        content=ft.Column([
            ft.Container(height=60),
            ft.Text("🌤️", size=90),
            ft.Text("Smart Assistant", size=34, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Text("Your Daily Companion", size=16, color=ft.Colors.WHITE70),
            ft.Container(height=20),
            ft.Text("Keep yourself on the track!", size=18, weight=ft.FontWeight.W_500, 
                   color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
            ft.Container(height=30),
            name_input,
            ft.Container(height=20),
            ft.FilledButton(
                "Get Started",
                on_click=start_app,
                width=220,
                height=50,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.WHITE,
                    color="#DB5C40",
                    shape=ft.RoundedRectangleBorder(radius=30),
                ),
            ),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
    )

    # ========== MAIN APP SCREEN ==========
    time_text = ft.Text("", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
    date_text = ft.Text("", size=16, color=ft.Colors.GREY_800)
    quote_text = ft.Text(random.choice(QUOTES), size=13, italic=True, 
                         color=ft.Colors.GREY_700, text_align=ft.TextAlign.CENTER)

    def update_quote():
        quote_text.value = random.choice(QUOTES)
        page.update()

    def start_motivation_rotation():
        def _rotate():
            while True:
                time.sleep(30)
                update_quote()
        threading.Thread(target=_rotate, daemon=True).start()

    def update_time():
        now = datetime.now()
        time_text.value = now.strftime("%I:%M:%S %p")
        date_text.value = now.strftime("%A, %B %d, %Y")
        page.update()

    def start_time_updates():
        def _update():
            while True:
                update_time()
                time.sleep(1)
        threading.Thread(target=_update, daemon=True).start()

    # ========== TASK MANAGEMENT ==========
    tasks_list = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
    task_count_text = ft.Text("0 tasks", size=14, color=ft.Colors.GREY_700)

    def update_task_count():
        count = len(tasks_list.controls)
        task_count_text.value = f"{count} task{'s' if count != 1 else ''}"
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
            # Create row components
            checkbox = ft.Checkbox(value=False, check_color=ft.Colors.BLUE_700)
            task_label = ft.Text(task_title.value, size=16, expand=True)
            delete_btn = ft.TextButton("🗑️", style=ft.ButtonStyle(color=ft.Colors.RED_400))
            
            # Create row container
            row = ft.Container(
                content=ft.Row([checkbox, task_label, delete_btn], 
                              alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor=ft.Colors.WHITE,
                padding=10,
                border_radius=12,
            )
            
            # Delete function
            def delete_clicked(ev):
                tasks_list.controls.remove(row)
                update_task_count()
                page.update()
            
            delete_btn.on_click = delete_clicked
            
            # Mark complete function
            def toggle_complete(ev):
                if checkbox.value:
                    task_label.style = ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH, 
                                                    color=ft.Colors.GREY_500)
                else:
                    task_label.style = ft.TextStyle(decoration=None, color=ft.Colors.BLACK)
                page.update()
            
            checkbox.on_change = toggle_complete
            
            tasks_list.controls.append(row)
            task_title.value = ""
            update_task_count()
            page.update()

    def clear_all(e):
        tasks_list.controls.clear()
        update_task_count()
        page.update()

    # ========== WEATHER SECTION ==========
    weather_text = ft.Text("Loading...", size=15, color=ft.Colors.GREY_800)

    def update_weather():
        weather_text.value = get_weather()
        page.update()

    # ========== MAIN LAYOUT ==========
    main_container.content = ft.Column([
        # Header
        ft.Container(
            content=ft.Column([
                ft.Row([ft.Text("🌤️", size=36), greeting_name], 
                       alignment=ft.MainAxisAlignment.CENTER),
                time_text,
                date_text,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                quote_text,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.Colors.BLUE_50,
            padding=20,
            border_radius=15,
        ),
        
        # Tasks section
        ft.Row([ft.Text("📋 My Tasks", size=20, weight=ft.FontWeight.BOLD), task_count_text],
               alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Row([task_title, ft.TextButton("➕ Add", on_click=add_task, 
                                         style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_600, 
                                                             color=ft.Colors.WHITE, 
                                                             shape=ft.RoundedRectangleBorder(radius=25)))]),
        ft.Row([ft.TextButton("🗑️ Clear all", on_click=clear_all, 
                             style=ft.ButtonStyle(color=ft.Colors.RED_600))], 
               alignment=ft.MainAxisAlignment.END),
        ft.Container(
            content=tasks_list,
            height=280,
            bgcolor=ft.Colors.GREY_100,
            border_radius=15,
            padding=10,
        ),
        
        # Weather section
        ft.Container(
            content=ft.Column([
                ft.Row([ft.Text("☁️", size=20), ft.Text("Weather Advice", size=16, 
                                                        weight=ft.FontWeight.BOLD)]),
                weather_text,
                ft.TextButton("Refresh", on_click=lambda e: update_weather(),
                             style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_500, color=ft.Colors.WHITE)),
            ], spacing=8),
            bgcolor=ft.Colors.ORANGE_100,
            padding=15,
            border_radius=15,
        ),
    ], scroll=ft.ScrollMode.AUTO, expand=True)

    # Start everything
    page.add(welcome_container, main_container)
    update_time()
    quote_text.value = random.choice(QUOTES)

if __name__ == "__main__":
    ft.app(target=main)