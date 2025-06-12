import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from middleware import module_project, module_user

class BaseMainScreen(ctk.CTkFrame):
    """Lớp cơ sở chứa các thành phần chung cho MainScreen và AdminScreen."""
    def __init__(self, master, app, user_info, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self.user_info = user_info
        self.logger = app.logger
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar (thanh bên trái) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        welcome_text = f"Xin chào,\n{self.user_info.get('name', 'User')}"
        self.welcome_label = ctk.CTkLabel(self.sidebar_frame, text=welcome_text, font=ctk.CTkFont(size=20, weight="bold"))
        self.welcome_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.new_project_button = ctk.CTkButton(self.sidebar_frame, text="Tạo dự án mới", command=self.open_create_project_dialog)
        self.new_project_button.grid(row=1, column=0, padx=20, pady=10)
        
        self.profile_button = ctk.CTkButton(self.sidebar_frame, text="Thông tin cá nhân", command=self.app.show_profile_screen)
        self.profile_button.grid(row=2, column=0, padx=20, pady=10)

        self.logout_button = ctk.CTkButton(self.sidebar_frame, text="Đăng xuất", fg_color="transparent", border_width=2, command=self.app.logout)
        self.logout_button.grid(row=5, column=0, padx=20, pady=20, sticky="s")
        
        # --- Main content area (khu vực chính bên phải) ---
        self.main_content_frame = ctk.CTkScrollableFrame(self, label_text="Danh sách dự án")
        self.main_content_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_content_frame.grid_columnconfigure(0, weight=1)
        
        self.load_projects()

    def load_projects(self):
        for widget in self.main_content_frame.winfo_children():
            widget.destroy()

        projects = module_project.get_all_projects()
        current_user_id = self.user_info.get("id")

        for project in projects:
            member_ids = [member['id'] for member in project.get('members', [])]
            if current_user_id in member_ids:
                self.create_project_widget(project)

    def create_project_widget(self, project):
        project_frame = ctk.CTkFrame(self.main_content_frame, corner_radius=10)
        project_frame.pack(fill="x", pady=5, padx=5)
        
        project_name = ctk.CTkLabel(project_frame, text=project.get('name', 'N/A'), font=ctk.CTkFont(size=16, weight="bold"))
        project_name.pack(anchor="w", padx=15, pady=(10, 5))
        
        project_desc = ctk.CTkLabel(project_frame, text=project.get('description', 'No description'), anchor="w")
        project_desc.pack(anchor="w", padx=15, pady=(0, 10))

        button_frame = ctk.CTkFrame(project_frame, fg_color="transparent")
        button_frame.pack(anchor="e", padx=15, pady=(0, 10))

        view_button = ctk.CTkButton(button_frame, text="Xem", width=80, command=lambda p=project: self.app.show_project_detail_screen(p.get('projectID')))
        view_button.pack(side="left", padx=5)

        if self.user_info.get("id") == project.get("ownerID"):
            edit_button = ctk.CTkButton(button_frame, text="Sửa", width=80, command=lambda p=project: self.open_edit_project_dialog(p))
            edit_button.pack(side="left", padx=5)

            delete_button = ctk.CTkButton(button_frame, text="Xóa", fg_color="#D32F2F", hover_color="#B71C1C", width=80, command=lambda p_id=project.get('projectID'): self.delete_project(p_id))
            delete_button.pack(side="left", padx=5)

    def open_create_project_dialog(self):
        # ... (implementation)
        pass

    def open_edit_project_dialog(self, project):
        # ... (implementation)
        pass

    def delete_project(self, project_id):
        # ... (implementation)
        pass

class MainScreen(BaseMainScreen):
    """Màn hình chính cho người dùng thông thường."""
    def __init__(self, master, app, user_info, **kwargs):
        super().__init__(master, app, user_info, **kwargs)

class AdminScreen(BaseMainScreen):
    """Màn hình chính cho quản trị viên."""
    def __init__(self, master, app, user_info, **kwargs):
        super().__init__(master, app, user_info, **kwargs)
        
        # --- [ĐÃ XÓA] Nút Quản lý người dùng ---
        # self.user_mgnt_button = ctk.CTkButton(self.sidebar_frame, text="Quản lý người dùng", command=self.app.show_user_management_screen)
        # self.user_mgnt_button.grid(row=3, column=0, padx=20, pady=10)

    # Admin có thể xem tất cả project
    def load_projects(self):
        for widget in self.main_content_frame.winfo_children():
            widget.destroy()

        projects = module_project.get_all_projects()
        for project in projects:
            self.create_project_widget(project)
