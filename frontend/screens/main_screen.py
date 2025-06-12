import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from middleware.module_project import get_all_projects, create_project, delete_project, update_project

class MainScreen(ctk.CTkFrame):
    def __init__(self, master, app, user_info, **kwargs):
        super().__init__(master)
        self.app = app
        self.logger = app.logger
        self.user_info = user_info
        self.pack(fill="both", expand=True)
        self.create_widgets()
        self.refresh_projects()

    def create_widgets(self):
        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        ctk.CTkLabel(self.sidebar_frame, text=f"Xin chào,\n{self.user_info.get('name')}", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10))
        ctk.CTkButton(self.sidebar_frame, text="Tạo dự án mới", command=self.open_add_project_form).grid(row=1, column=0, padx=20, pady=10)
        ctk.CTkButton(self.sidebar_frame, text="Thông tin cá nhân", state="disabled").grid(row=2, column=0, padx=20, pady=10)
        ctk.CTkButton(self.sidebar_frame, text="Đăng xuất", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), command=self.app.logout).grid(row=5, column=0, padx=20, pady=20, sticky="s")
        
        # --- Main Content ---
        self.main_content_frame = ctk.CTkScrollableFrame(self)
        self.main_content_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        self.project_list_frame = ctk.CTkFrame(self.main_content_frame, fg_color="transparent")
        self.project_list_frame.pack(fill="both", expand=True)

    def refresh_projects(self):
        """Làm mới danh sách dự án cho Member."""
        for widget in self.project_list_frame.winfo_children(): widget.destroy()
        all_projects = get_all_projects()
        member_projects = []
        for p in all_projects:
            # Sửa lại logic để duyệt qua danh sách object member
            member_ids = [member.get('id') for member in p.get('members', [])]
            if self.user_info.get('id') in member_ids:
                member_projects.append(p)
        self.display_projects(member_projects, "Bạn chưa tham gia vào dự án nào.")

    def display_projects(self, project_list, no_project_message):
        """Hàm chung để hiển thị danh sách các dự án."""
        if not project_list:
            ctk.CTkLabel(self.project_list_frame, text=no_project_message, font=("Arial", 16)).pack(pady=20)
            return
        for project_data in project_list:
            card = self.create_project_card(self.project_list_frame, project_data)
            card.pack(fill="x", pady=5, padx=5)

    def create_project_card(self, master, project_data):
        """Tạo một card dự án với đầy đủ thông tin và nút bấm."""
        card = ctk.CTkFrame(master, border_width=1, corner_radius=8)
        
        ctk.CTkLabel(card, text=project_data.get("name", "N/A"), font=ctk.CTkFont(size=16, weight="bold"), anchor="w").pack(fill="x", padx=10, pady=(10,5))
        ctk.CTkLabel(card, text=project_data.get("description", ""), wraplength=700, justify="left", anchor="w").pack(fill="x", padx=10, pady=(0, 10))
        
        button_frame = ctk.CTkFrame(card, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        # Sử dụng đúng key 'projectID' và 'ownerID' từ JSON
        ctk.CTkButton(button_frame, text="Xem", width=60, command=lambda p=project_data: self.app.show_project_detail_screen(p.get('projectID'))).pack(side="left")
        
        if self.user_info.get('id') == project_data.get('ownerID') or self.user_info.get('role') == "Admin":
            ctk.CTkButton(button_frame, text="Sửa", width=60, command=lambda p=project_data: self.open_edit_project_form(p)).pack(side="left", padx=5)
            ctk.CTkButton(button_frame, text="Xóa", width=60, fg_color="#D83E3E", hover_color="#B22222", command=lambda pid=project_data.get("projectID"): self.confirm_delete_project(pid)).pack(side="left", padx=5)
            
        return card

    def open_add_project_form(self):
        """Mở dialog để thêm dự án mới."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Tạo dự án mới"); dialog.geometry("400x300"); dialog.transient(self.app); dialog.grab_set()
        
        ctk.CTkLabel(dialog, text="Tên dự án:").pack(pady=(10, 0), padx=20, anchor="w")
        name_entry = ctk.CTkEntry(dialog, width=360); name_entry.pack(pady=5, padx=20)
        ctk.CTkLabel(dialog, text="Mô tả:").pack(pady=(10, 0), padx=20, anchor="w")
        desc_textbox = ctk.CTkTextbox(dialog, width=360, height=100); desc_textbox.pack(pady=5, padx=20)

        def submit():
            name, desc = name_entry.get(), desc_textbox.get("1.0", "end-1c")
            if not name:
                CTkMessagebox(master=dialog, title="Lỗi", message="Tên dự án không được để trống!", icon="cancel")
                return

            # =============================================================
            # ==================== LOGIC ĐƯỢC CẬP NHẬT =====================
            # =============================================================
            # Hàm create_project giờ sẽ trả về project_id hoặc None
            new_project_id = create_project(name, desc, self.user_info.get('id'))
            if new_project_id:
                CTkMessagebox(master=dialog, title="Thành công", message="Tạo dự án thành công!")
                dialog.destroy()
                self.refresh_projects() # Làm mới danh sách để thấy dự án mới
            else:
                CTkMessagebox(master=dialog, title="Lỗi", message="Có lỗi xảy ra khi tạo dự án!", icon="cancel")
            # =============================================================
        
        ctk.CTkButton(dialog, text="Tạo dự án", command=submit).pack(pady=20)

    def confirm_delete_project(self, project_id):
        """Hỏi xác nhận trước khi xóa dự án."""
        if not project_id: return
        msg = CTkMessagebox(title="Xác nhận", message="Bạn có chắc chắn muốn xóa dự án này?", icon="warning", option_1="Hủy", option_2="Xóa")
        if msg.get() == "Xóa":
            if delete_project(project_id):
                CTkMessagebox(title="Thành công", message="Đã xóa dự án.")
                self.refresh_projects()
            else:
                CTkMessagebox(title="Lỗi", message="Xóa dự án thất bại.", icon="cancel")

    def open_edit_project_form(self, project_data):
        """Mở dialog để sửa thông tin dự án."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Chỉnh sửa Dự án"); dialog.geometry("400x300"); dialog.transient(self.app); dialog.grab_set()
        
        ctk.CTkLabel(dialog, text="Tên dự án:").pack(pady=(10, 0), padx=20, anchor="w")
        name_entry = ctk.CTkEntry(dialog, width=360); name_entry.insert(0, project_data.get("name")); name_entry.pack(pady=5, padx=20)
        
        ctk.CTkLabel(dialog, text="Mô tả:").pack(pady=(10, 0), padx=20, anchor="w")
        desc_textbox = ctk.CTkTextbox(dialog, width=360, height=100); desc_textbox.insert("1.0", project_data.get("description")); desc_textbox.pack(pady=5, padx=20)

        def save():
            new_name, new_desc = name_entry.get(), desc_textbox.get("1.0", "end-1c")
            if new_name and update_project(project_data.get("projectID"), new_name, new_desc):
                CTkMessagebox(title="Thành công", message="Cập nhật thành công!", master=dialog)
                dialog.destroy()
                self.refresh_projects()
            else:
                CTkMessagebox(title="Lỗi", message="Tên không được trống hoặc có lỗi xảy ra.", icon="cancel", master=dialog)
        
        ctk.CTkButton(dialog, text="Lưu thay đổi", command=save).pack(pady=20)

class AdminScreen(MainScreen):
    """Màn hình dành cho Admin, kế thừa từ MainScreen và có thêm chức năng."""
    def create_widgets(self):
        super().create_widgets()
        ctk.CTkButton(self.sidebar_frame, text="Quản lý người dùng", command=self.open_user_management).grid(row=3, column=0, padx=20, pady=10)

    def refresh_projects(self):
        """Admin thấy tất cả các dự án."""
        for widget in self.project_list_frame.winfo_children(): widget.destroy()
        all_projects = get_all_projects()
        self.display_projects(all_projects, "Chưa có dự án nào trong hệ thống.")
    
    def open_user_management(self):
        """Chuyển đến màn hình quản lý người dùng."""
        self.app.show_user_management_screen()