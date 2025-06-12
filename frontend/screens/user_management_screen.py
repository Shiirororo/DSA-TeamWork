import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from middleware.module_user import get_all_users, update_user_role, delete_user

class EditRoleDialog(ctk.CTkToplevel):
    """Dialog tùy chỉnh để sửa vai trò người dùng."""
    def __init__(self, master, user_name, current_role):
        super().__init__(master)
        self.new_role = None
        self.title("Thay đổi vai trò"); self.geometry("350x180"); self.transient(master); self.grab_set()
        
        ctk.CTkLabel(self, text=f"Chọn vai trò mới cho {user_name}:").pack(padx=20, pady=(20, 10))
        self.role_combo = ctk.CTkComboBox(self, values=["Admin", "Member"])
        self.role_combo.set(current_role)
        self.role_combo.pack(padx=20, pady=5)
        
        button_frame = ctk.CTkFrame(self, fg_color="transparent"); button_frame.pack(pady=20)
        ctk.CTkButton(button_frame, text="Lưu", command=self.on_save).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Hủy", fg_color="gray", command=self.destroy).pack(side="left", padx=10)

    def on_save(self):
        self.new_role = self.role_combo.get()
        self.destroy()

    def get_input(self):
        """Chờ cho đến khi dialog đóng và trả về kết quả."""
        self.master.wait_window(self)
        return self.new_role

class UserManagementScreen(ctk.CTkFrame):
    def __init__(self, master, app, user_info, **kwargs):
        super().__init__(master)
        self.app = app
        self.logger = app.logger
        self.user_info = user_info
        self.pack(fill="both", expand=True)
        self.create_widgets()
        self.refresh_user_list()

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self); main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent"); header_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkButton(header_frame, text="< Quay lại", width=100, command=self.app.show_main_menu).pack(side="left")
        ctk.CTkLabel(header_frame, text="Quản lý Người dùng", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left", expand=True, padx=20)
        
        self.scrollable_frame = ctk.CTkScrollableFrame(main_frame)
        self.scrollable_frame.pack(fill="both", expand=True)

    def refresh_user_list(self):
        for widget in self.scrollable_frame.winfo_children(): widget.destroy()
        for user_data in get_all_users():
            self.create_user_card(user_data).pack(fill="x", padx=10, pady=5)

    def create_user_card(self, user_data):
        card = ctk.CTkFrame(self.scrollable_frame, border_width=1)
        
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="both", expand=True, padx=10, pady=10)
        info_frame.columnconfigure(0, weight=3); info_frame.columnconfigure(1, weight=2); info_frame.columnconfigure(2, weight=1)
        
        ctk.CTkLabel(info_frame, text=f"{user_data['name']} ({user_data['email']})", anchor="w").grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(info_frame, text=f"Vai trò: {user_data['role']}", anchor="w").grid(row=0, column=1, sticky="ew", padx=10)
        
        btn_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        btn_frame.grid(row=0, column=2, sticky="e")
        
        is_self = (user_data['id'] == self.user_info['id'])
        
        ctk.CTkButton(btn_frame, text="Sửa vai trò", width=100, command=lambda u=user_data: self.open_edit_role_dialog(u), state="disabled" if is_self else "normal").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Xóa", width=60, fg_color="#D83E3E", hover_color="#B22222", command=lambda u=user_data: self.confirm_delete_user(u), state="disabled" if is_self else "normal").pack(side="left", padx=5)
        
        return card

    def open_edit_role_dialog(self, user_data):
        dialog = EditRoleDialog(self.app, user_name=user_data['name'], current_role=user_data['role'])
        new_role = dialog.get_input()
        
        if new_role and new_role != user_data['role']:
            if update_user_role(user_data['id'], new_role):
                CTkMessagebox(title="Thành công", message="Cập nhật vai trò thành công.")
                self.refresh_user_list()
            else:
                CTkMessagebox(title="Lỗi", message="Cập nhật vai trò thất bại.", icon="cancel")

    def confirm_delete_user(self, user_data):
        msg = CTkMessagebox(title="Xác nhận", message=f"Bạn có chắc muốn xóa '{user_data['name']}'?", icon="warning", option_1="Hủy", option_2="Xóa")
        if msg.get() == "Xóa":
            if delete_user(user_data['id']):
                CTkMessagebox(title="Thành công", message="Đã xóa người dùng.")
                self.refresh_user_list()
            else:
                CTkMessagebox(title="Lỗi", message="Xóa người dùng thất bại.", icon="cancel")