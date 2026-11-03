import flet as ft
from users import validate_user
#sys.path.append(os.path.dirname(os.path.abspath(__file__)))


    
class LoginView(ft.Card):
    def __init__(self, state, on_login_success):
        super().__init__()
        self.state = state
        self.on_login_success = on_login_success
        
        self.username_input = ft.TextField(label="Username", width=300, prefix_icon=ft.Icons.PERSON)
        self.password_input = ft.TextField(label="Password", password=True, can_reveal_password=True, width=300, prefix_icon=ft.Icons.LOCK)
        self.msg = ft.Text(value="", size=14, weight=ft.FontWeight.BOLD)

        self.username_input.value = "admin"
        self.password_input.value =  "admin123"   
        
        self.content = ft.Container(
            content=ft.Column([
                ft.Text("Secure Authorization Login", size=22, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                self.username_input,
                self.password_input,
                ft.Container(height=10),
                ft.Row([
                    ft.Button(content=ft.Text("Submit"), on_click=self.handle_submit, style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE, elevation=2)),
                    ft.Button(content=ft.Text("Clear"), on_click=self.handle_clear, style=ft.ButtonStyle(elevation=0)),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                ft.Container(height=10),
                self.msg
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=30,
        )

    def handle_submit(self, e):
        username = self.username_input.value.strip()
        password = self.password_input.value.strip()
        
        if not username or not password:
            self.msg.value = "Fields cannot be blank."
            self.msg.color = ft.Colors.ORANGE_700
            self.update()
            return
            
        if validate_user(username, password):
            self.state.current_user = username
            self.on_login_success()
        else:
            self.msg.value = "Invalid credentials."
            self.msg.color = ft.Colors.RED_700
            self.update()

    def handle_clear(self, e):
        self.username_input.value = ""
        self.password_input.value = ""
        self.msg.value = ""
        self.update()
