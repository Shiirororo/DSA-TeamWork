import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from middleware import module_project, module_user

class CreateProjectDialog(ctk.CTkToplevel):
    """
    Một cửa sổ dialog tùy chỉnh để tạo dự án mới.
    """
    def __init__(self, master, app, on_success_callback):
        super().__init__(master)
        self.app = app
        self.on_success = on_success_callback # Hàm để làm mới danh sách project
        
        self.title("Tạo dự án mới")
        self.geometry("400x300")
        self.transient(master)
        self.grab_set()

        ctk.CTkLabel(self, text="Tên dự án:", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5), padx=20, anchor="w")
        self.name_entry = ctk.CTkEntry(self, placeholder_text="Ví dụ: Xây dựng ứng dụng quản lý...")
        self.name_entry.pack(pady=5, padx=20, fill="x")
        
        ctk.CTkLabel(self, text="Mô tả (tùy chọn):", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5), padx=20, anchor="w")
        self.desc_textbox = ctk.CTkTextbox(self, height=80)
        self.desc_textbox.pack(pady=5, padx=20, fill="x", expand=True)
        
        self.create_button = ctk.CTkButton(self, text="Tạo dự án", command=self.submit)
        self.create_button.pack(pady=20)

    def submit(self):
        project_name = self.name_entry.get()
        project_desc = self.desc_textbox.get("1.0", "end-1c").strip()
        
        if not project_name:
            CTkMessagebox(master=self, title="Lỗi", message="Tên dự án không được để trống.", icon="cancel")
            return
            
        owner_id = self.app.user_info.get("id")
        # Giả định module_project.create_project chỉ cần name, description, owner_id
        if module_project.create_project(project_name, project_desc, owner_id):
            CTkMessagebox(title="Thành công", message="Đã tạo dự án thành công!", master=self.app)
            self.on_success() # Gọi hàm làm mới danh sách
            self.destroy() # Đóng dialog
        else:
            CTkMessagebox(master=self, title="Lỗi", message="Không thể tạo dự án.", icon="cancel")


class BaseMainScreen(ctk.CTkFrame):
    """Lớp cơ sở chứa các thành phần chung cho MainScreen và AdminScreen."""
    def __init__(self, master, app, user_info, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self.user_info = user_info
        self.logger = app.logger
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(3, weight=1)

        welcome_text = f"Xin chào,\n{self.user_info.get('name', 'User')}"
        self.welcome_label = ctk.CTkLabel(self.sidebar_frame, text=welcome_text, font=ctk.CTkFont(size=20, weight="bold"))
        self.welcome_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.new_project_button = ctk.CTkButton(self.sidebar_frame, text="Tạo dự án mới", command=self.open_create_project_dialog)
        self.new_project_button.grid(row=1, column=0, padx=20, pady=10)
        
        self.profile_button = ctk.CTkButton(self.sidebar_frame, text="Thông tin cá nhân", command=self.app.show_profile_screen)
        self.profile_button.grid(row=2, column=0, padx=20, pady=10)

        self.logout_button = ctk.CTkButton(self.sidebar_frame, text="Đăng xuất", fg_color="transparent", border_width=2, command=self.app.logout)
        self.logout_button.grid(row=4, column=0, padx=20, pady=20, sticky="s")
        
        # --- Main content area ---
        self.main_content_frame = ctk.CTkScrollableFrame(self, label_text="Danh sách dự án")
        self.main_content_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_content_frame.grid_columnconfigure(0, weight=1)
        
        self.load_projects()

    def open_create_project_dialog(self):
        """Mở dialog tùy chỉnh để tạo dự án mới."""
        CreateProjectDialog(self.app, self.app, on_success_callback=self.load_projects)
        
    def load_projects(self):
        """Tải và hiển thị danh sách các dự án."""
        # Xóa các project cũ trước khi tải lại
        for widget in self.main_content_frame.winfo_children():
            widget.destroy()

        projects = module_project.get_all_projects()
        current_user_id = self.user_info.get("id")

        for project in projects:
            # User thường chỉ thấy project họ là thành viên
            member_ids = [member['id'] for member in project.get('members', [])]
            if self.user_info.get('role') in ['Admin', 'Super Admin'] or current_user_id in member_ids:
                self.create_project_widget(project)
    
    def create_project_widget(self, project):
        """Tạo một widget cho mỗi dự án trong danh sách."""
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

        # Chỉ Owner mới có quyền sửa, xóa
        if self.user_info.get("id") == project.get("ownerID"):
            edit_button = ctk.CTkButton(button_frame, text="Sửa", width=80, command=lambda p=project: self.open_edit_project_dialog(p))
            edit_button.pack(side="left", padx=5)

            delete_button = ctk.CTkButton(button_frame, text="Xóa", fg_color="#D32F2F", hover_color="#B71C1C", width=80, command=lambda p_id=project.get('projectID'): self.delete_project(p_id))
            delete_button.pack(side="left", padx=5)

    def open_edit_project_dialog(self, project):
        """Mở dialog để sửa thông tin dự án."""
        dialog = ctk.CTkInputDialog(text="Nhập tên dự án mới:", title="Sửa dự án")
        new_name = dialog.get_input()
        if new_name:
            desc_dialog = ctk.CTkInputDialog(text="Nhập mô tả mới:", title="Sửa mô tả")
            new_desc = desc_dialog.get_input()
            if module_project.update_project(project.get("projectID"), new_name, new_desc or ""):
                 CTkMessagebox(title="Thành công", message="Cập nhật dự án thành công!", master=self.app)
                 self.load_projects()
            else:
                CTkMessagebox(title="Lỗi", message="Không thể cập nhật dự án.", icon="cancel", master=self.app)

    def delete_project(self, project_id):
        """Xử lý logic xóa dự án."""
        msg = CTkMessagebox(title="Xác nhận xóa", message="Bạn có chắc chắn muốn xóa dự án này không?",
                            icon="warning", option_1="Hủy", option_2="Xóa", master=self.app)
        if msg.get() == "Xóa":
            if module_project.delete_project(project_id):
                CTkMessagebox(title="Thành công", message="Đã xóa dự án.", master=self.app)
                self.load_projects()
            else:
                CTkMessagebox(title="Lỗi", message="Không thể xóa dự án.", icon="cancel", master=self.app)


class MainScreen(BaseMainScreen):
    """Màn hình chính cho người dùng thông thường."""
    def __init__(self, master, app, user_info, **kwargs):
        super().__init__(master, app, user_info, **kwargs)

class AdminScreen(BaseMainScreen):
    """Màn hình chính cho quản trị viên."""
    def __init__(self, master, app, user_info, **kwargs):
        super().__init__(master, app, user_info, **kwargs)
        # Nút Quản lý người dùng đã được loại bỏ ở các phiên bản trước
        # Nếu muốn thêm lại, có thể đặt ở đây
