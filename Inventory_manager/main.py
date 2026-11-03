#sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Get the exact absolute directory path of main.py
#CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Inject it at index 0 so it takes priority over global virtual env lookups
#if CURRENT_DIR not in sys.path:
    #sys.path.insert(0, CURRENT_DIR)
import os
import flet as ft
from database import init_db
from models import AppState
from ui_login import LoginView
from ui_dashboard import DashboardView

def main(page: ft.Page):
    # Setup standard database layout
    init_db()

    # Configure viewport windows
    page.title = "Enterprise Inventory Workspace Manager"
    page.window_width = 950
    page.window_height = 650
    
    # Initialize common app state context container
    state = AppState()

    def show_dashboard():
        page.controls.clear()
        page.vertical_alignment = ft.MainAxisAlignment.START
        page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
        page.add(DashboardView(page, state, on_logout=show_login))

    def show_login():
        page.controls.clear()
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.add(LoginView(state, on_login_success=show_dashboard))

    # Trigger starting route framework panel view
    show_login()
    #show_dashboard()
    #db_path = os.path.abspath("stacks.db")
    #print(f"Your database is located at: {db_path}")

if __name__ == "__main__":
    ft.run(main)
