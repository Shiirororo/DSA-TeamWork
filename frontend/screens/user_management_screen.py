import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from middleware import module_user

class EditRoleDialog(ctk.CTkToplevel):
    """Một cửa sổ dialog để thay đổi vai trò của người dùng."""
    def __init__(self, master, app, user, callback):
        super().__init__(master)
        self.app = app
        self.user = user
        self.callback = callback # Hàm để tải lại danh sách sau khi sửa
        self.logger = app.logger
        
        self.title("Thay đổi vai trò")
        self.geometry("350x200")
        self.transient(master) # Dialog này sẽ luôn ở trên cửa sổ chính
        self.grab_set() # Chặn tương tác với cửa sổ chính

        ctk.CTkLabel(self, text=f"Chọn vai trò mới cho {self.user.get('name')}:").pack(pady=10)
        
        # Super Admin có thể thăng cấp người khác thành Admin
        available_roles = ["User", "Admin"]
        self.role_combo = ctk.CTkComboBox(self, values=available_roles)
        self.role_combo.set(self.user.get("role", "User"))
        self.role_combo.pack(pady=10, padx=20, fill="x")

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=20)
        ctk.CTkButton(button_frame, text="Lưu", command=self.save_role).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Hủy", fg_color="gray", command=self.destroy).pack(side="left", padx=10)
    
    def save_role(self):
        new_role = self.role_combo.get()
        user_id = self.user.get("id")
        
        success, message = module_user.update_user_role(user_id, new_role)
        if success:
            CTkMessagebox(title="Thành công", message=message, master=self.app)
            self.callback() # Tải lại danh sách người dùng ở màn hình chính
            self.destroy()
        else:
            CTkMessagebox(title="Lỗi", message=message, icon="cancel", master=self.app)


class UserManagementScreen(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self.logger = app.logger

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        ctk.CTkLabel(header_frame, text="Quản lý người dùng", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        
        back_button = ctk.CTkButton(header_frame, text="Quay lại", command=self.app.show_main_menu, width=100)
        back_button.pack(side="right")

        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.load_users()

    def load_users(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        users = module_user.get_all_users()
        for user in users:
            self.create_user_widget(user)

    def create_user_widget(self, user):
        user_frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=10)
        user_frame.pack(fill="x", pady=5, padx=5)
        user_frame.grid_columnconfigure(1, weight=1)

        info_text = f"{user.get('name', 'N/A')} ({user.get('role', 'N/A')})\nEmail: {user.get('email', 'N/A')}"
        name_label = ctk.CTkLabel(user_frame, text=info_text, justify="left")
        name_label.grid(row=0, column=0, sticky="w", padx=15, pady=10)
        
        button_frame = ctk.CTkFrame(user_frame, fg_color="transparent")
        button_frame.grid(row=0, column=1, sticky="e", padx=15, pady=10)
        
        # Logic phân quyền hiển thị nút
        is_target_super_admin = user.get("role") == "Super Admin"

        # Nút "Sửa vai trò" chỉ hiển thị khi mục tiêu không phải là Super Admin
        if not is_target_super_admin:
            edit_button = ctk.CTkButton(button_frame, text="Sửa vai trò", command=lambda u=user: self.open_edit_role_dialog(u))
            edit_button.pack(side="left", padx=5)

        # Nút "Xóa" chỉ hiển thị khi mục tiêu không phải là Super Admin VÀ không phải là chính người dùng đang đăng nhập
        if not is_target_super_admin and user.get("id") != self.app.user_info.get("id"):
            delete_button = ctk.CTkButton(button_frame, text="Xóa", fg_color="#D32F2F", hover_color="#B71C1C", command=lambda u_id=user.get('id'): self.delete_user(u_id))
            delete_button.pack(side="left", padx=5)
    
    def open_edit_role_dialog(self, user):
        EditRoleDialog(self, self.app, user, self.load_users)

    def delete_user(self, user_id):
        msg = CTkMessagebox(title="Xác nhận xóa", message="Bạn có chắc chắn muốn xóa người dùng này không?",
                            icon="warning", option_1="Hủy", option_2="Xóa", master=self.app)
        if msg.get() == "Xóa":
            # Xử lý kết quả trả về từ middleware
            success, message = module_user.delete_user(user_id)
            if success:
                CTkMessagebox(title="Thành công", message=message, master=self.app)
                self.load_users()
            else:
                CTkMessagebox(title="Lỗi", message=message, icon="cancel", master=self.app)
