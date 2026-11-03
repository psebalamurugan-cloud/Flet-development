import csv
import flet as ft
from database import add_item, get_active_items, get_all_active_items_detailed, update_item, delete_item

class DashboardView(ft.Column):
    def __init__(self, page: ft.Page, state, on_logout):
        super().__init__(expand=True)
        # CHANGED: Renamed from self.page to self.current_page to prevent Flet framework conflict
        self.current_page = page 
        self.state = state
        self.on_logout = on_logout
        
        # Form UI Components
        self.code_input = ft.TextField(label="Item Code", width=250)
        self.code_input.visible = False
        self.code_input.value ="A0000"
        self.name_input = ft.TextField(label="Item Name", width=250, max_length=45, counter=ft.Container(), hint_text="Max 40 chars",)
        #self.volume_input = ft.TextField(
        #                        label="Volume in ml/gm (eg:10 ml or 10 gm)", 
        #                        input_filter=ft.InputFilter(
        #                            allow=True, 
        #                           regex_string=r"^[0-9]*$", 
        #                            replacement_string=""
        #                        ), width=250)
        self.volume_input = ft.TextField(label="Vol in ml/gm/lt (eg:100 ml)", width=250, max_length=8, counter=ft.Container(),
                                         hint_text="Max 8 chars",
                                         )
        self.form_msg = ft.Text(value="", size=14, weight=ft.FontWeight.BOLD)
        self.submit_btn = ft.Button(content=ft.Text("Submit Item"), on_click=self.handle_form_submit, style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_700, elevation=2))
        
        # Interactive Table Element
        self.items_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Item Code")),
                ft.DataColumn(ft.Text("Item Name")),
                ft.DataColumn(ft.Text("Volume")),
                ft.DataColumn(ft.Text("Actions")),
            ],
            rows=[]
        )
        
        # File Picker Attachment setups
        self.file_picker = ft.FilePicker(on_result=self.save_csv_export)
        #self.current_page.overlay.append(self.file_picker)

        self.build_ui()
        self.refresh_table()

    def build_ui(self):
        header = ft.Container(
            content=ft.Row([
                ft.Text("Inventory Control Center", size=18, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.Text(value=f"User: {self.state.current_user}", size=16, weight=ft.FontWeight.BOLD),
                    ft.IconButton(icon=ft.Icons.LOGOUT, icon_color=ft.Colors.RED, tooltip="Exit", on_click=lambda e: self.on_logout())
                ], spacing=15)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=15,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST
        )

        workspace_layout = ft.Row([
            # Input Control Block (Left Panel)
            ft.Container(
                content=ft.Column([
                    ft.Text("Add New / Modify Item", size=16, weight=ft.FontWeight.BOLD),
                    ft.Container(height=10),
                    self.code_input,
                    self.name_input,
                    self.volume_input,
                    ft.Container(height=10),
                    ft.Row([self.submit_btn, ft.Button(content=ft.Text("Clear Form"), on_click=lambda e: self.reset_form(), style=ft.ButtonStyle(elevation=0))], spacing=10),
                    ft.Container(height=15),
                    self.form_msg
                ]),
                padding=20, width=300, border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT), border_radius=8
            ),
            # View Active Inventory Block (Right Panel)
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("View Active Inventory Records", size=16, weight=ft.FontWeight.BOLD),
                        ft.Button(
                            content=ft.Row([ft.Icon(ft.Icons.DOWNLOAD, size=18), ft.Text("Export CSV")]),
                            on_click=lambda e: self.file_picker.save_file(file_name="active_inventory.csv", allowed_extensions=["csv"]),
                            style=ft.ButtonStyle(color=ft.Colors.BLUE_700, elevation=1)
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Container(height=10),
                    ft.ListView([self.items_table], expand=True)
                ]),
                padding=20, expand=True, border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT), border_radius=8
            )
        ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START, expand=True)

        self.controls = [header, ft.Container(content=workspace_layout, padding=20, expand=True)]

    def refresh_table(self):
        items = get_active_items()
        self.items_table.rows.clear()
        for code, name, vol in items:
            def edit_cb(c=code, n=name, v=vol): return lambda e: self.load_for_edit(c, n, v)
            def delete_cb(c=code): return lambda e: self.handle_delete(c)
            
            self.items_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(code)),
                    ft.DataCell(ft.Text(name)),
                    ft.DataCell(ft.Text(vol)),
                    ft.DataCell(ft.Row([
                        ft.IconButton(icon=ft.Icons.EDIT, icon_color=ft.Colors.BLUE, on_click=edit_cb()),
                        ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.RED, on_click=delete_cb())
                    ]))
                ])
            )
        self.current_page.update()

    def load_for_edit(self, code, name, vol):
        self.state.editing_code = code

        self.code_input.value = code
        self.code_input.disabled = True
        self.code_input.visible = True
        self.name_input.value = name
        self.volume_input.value = vol
        self.submit_btn.content = ft.Text("Update Item")
        self.form_msg.value = "Editing item mode active..."
        self.form_msg.color = ft.Colors.BLUE_700
        self.current_page.update()

    def reset_form(self):
        self.state.editing_code = None
        self.code_input.value = ""
        self.code_input.disabled = False
        self.code_input.visible = False
        self.name_input.value = ""
        self.volume_input.value = ""
        self.submit_btn.content = ft.Text("Submit Item")
        self.form_msg.value = ""
        self.current_page.update()

    def handle_form_submit(self, e):
        code = self.code_input.value.strip()
        name = self.name_input.value.strip()
        vol = self.volume_input.value.strip()

        if not name or not vol:
            self.form_msg.value = "All fields required."
            self.form_msg.color = ft.Colors.ORANGE_700
            self.current_page.update()
            return

        #if not code or not name or not vol:
        if not any(unit in vol.lower() for unit in ["ml", "gm", "lt"]):
            self.form_msg.value = "Add units like ml/gm/lt in volume."
            self.form_msg.color = ft.Colors.ORANGE_700
            self.current_page.update()
            return

        if self.state.editing_code is not None:
            update_item(self.state.editing_code, name, vol, self.state.current_user)
            self.form_msg.value = "Item metadata updated!"
            self.form_msg.color = ft.Colors.GREEN_700
            self.reset_form()
            self.refresh_table()
        else:
            success, msg = add_item(code, name, vol, self.state.current_user)
            self.form_msg.value = msg
            self.form_msg.color = ft.Colors.GREEN_700 if success else ft.Colors.RED_700
            if success:
                self.reset_form()
                self.refresh_table()

    def handle_delete(self, code):
        delete_item(code, self.state.current_user)
        self.form_msg.value = f"Item '{code}' deleted (state_active=1)."
        self.form_msg.color = ft.Colors.RED_600
        self.reset_form()
        self.refresh_table()

    def save_csv_export(self, e: ft.FilePickerResultEvent):
        if not e.path: return
        try:
            records = get_all_active_items_detailed()
            with open(e.path, mode='w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(["Item Code", "Item Name", "Volume", "State Active", "Created Date", "Created By", "Updated Date", "Updated By"])
                w.writerows(records)
            self.form_msg.value = "Data exported successfully!"
            self.form_msg.color = ft.Colors.GREEN_700
        except Exception as ex:
            self.form_msg.value = f"Export failed: {str(ex)}"
            self.form_msg.color = ft.Colors.RED_700
        self.current_page.update()
