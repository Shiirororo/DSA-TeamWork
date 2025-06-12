import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from middleware import module_user

class ProfileScreen(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master)
        self.app = app
        self.user_info = self.app.user_info
        self.logger = self.app.logger

        # --- Layout ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Header ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        ctk.CTkLabel(header_frame, text="Thông Tin Cá Nhân", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        
        back_button = ctk.CTkButton(header_frame, text="Quay lại", command=self.app.show_main_menu, width=100)
        back_button.pack(side="right")

        # --- Content Frame ---
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        content_frame.grid_columnconfigure(0, weight=1)
        # Center the content
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_rowconfigure(2, weight=1)
        
        main_form_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        main_form_frame.grid(row=1, column=0)


        # --- Khung hiển thị thông tin ---
        info_frame = ctk.CTkFrame(main_form_frame, corner_radius=10)
        info_frame.pack(pady=(0, 20), padx=40, fill="x")
        info_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(info_frame, text="Họ và tên:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", padx=15, pady=10)
        self.name_label = ctk.CTkLabel(info_frame, text=self.user_info.get("name", "N/A"), anchor="w")
        self.name_label.grid(row=0, column=1, sticky="ew", padx=15, pady=10)

        ctk.CTkLabel(info_frame, text="Tên đăng nhập:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, sticky="w", padx=15, pady=10)
        self.username_label = ctk.CTkLabel(info_frame, text=self.user_info.get("username", "N/A"), anchor="w")
        self.username_label.grid(row=1, column=1, sticky="ew", padx=15, pady=10)
        
        ctk.CTkLabel(info_frame, text="Vai trò:", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, sticky="w", padx=15, pady=10)
        self.role_label = ctk.CTkLabel(info_frame, text=self.user_info.get("role", "N/A"), anchor="w")
        self.role_label.grid(row=2, column=1, sticky="ew", padx=15, pady=10)

        # --- Khung đổi mật khẩu ---
        password_frame = ctk.CTkFrame(main_form_frame, corner_radius=10)
        password_frame.pack(pady=10, padx=40, fill="x")
        
        ctk.CTkLabel(password_frame, text="Đổi Mật Khẩu", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(10, 15), padx=15)

        ctk.CTkLabel(password_frame, text="Mật khẩu cũ").pack(anchor="w", padx=15)
        self.old_password_entry = ctk.CTkEntry(password_frame, show="*", width=400)
        self.old_password_entry.pack(pady=(0, 10), fill="x", padx=15)

        ctk.CTkLabel(password_frame, text="Mật khẩu mới").pack(anchor="w", padx=15)
        self.new_password_entry = ctk.CTkEntry(password_frame, show="*")
        self.new_password_entry.pack(pady=(0, 10), fill="x", padx=15)

        ctk.CTkLabel(password_frame, text="Xác nhận mật khẩu mới").pack(anchor="w", padx=15)
        self.confirm_password_entry = ctk.CTkEntry(password_frame, show="*")
        self.confirm_password_entry.pack(pady=(0, 10), fill="x", padx=15)

        save_button = ctk.CTkButton(password_frame, text="Lưu thay đổi", command=self.save_password)
        save_button.pack(pady=20, padx=15, anchor="e")
        
    def save_password(self):
        old_pw = self.old_password_entry.get()
        new_pw = self.new_password_entry.get()
        confirm_pw = self.confirm_password_entry.get()
        
        if not all([old_pw, new_pw, confirm_pw]):
            CTkMessagebox(title="Lỗi", message="Vui lòng điền đầy đủ các trường.", icon="cancel", master=self.app)
            return
            
        if len(new_pw) < 6:
            CTkMessagebox(title="Lỗi", message="Mật khẩu mới phải có ít nhất 6 ký tự.", icon="cancel", master=self.app)
            return

        if new_pw != confirm_pw:
            CTkMessagebox(title="Lỗi", message="Mật khẩu mới và xác nhận mật khẩu không khớp.", icon="cancel", master=self.app)
            return

        user_id = self.user_info.get("id")
        success, message = module_user.change_password(user_id, old_pw, new_pw)

        if success:
            CTkMessagebox(title="Thành công", message=message, master=self.app)
            self.old_password_entry.delete(0, 'end')
            self.new_password_entry.delete(0, 'end')
            self.confirm_password_entry.delete(0, 'end')
        else:
            CTkMessagebox(title="Lỗi", message=message, icon="cancel", master=self.app)
