import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from middleware import module_user

class LoginPage(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master)
        self.app = app
        self.logger = app.logger

        # --- Giao diện ---
        frame = ctk.CTkFrame(self)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame, text="Đăng Nhập", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(20, 20))
        
        ctk.CTkLabel(frame, text="Tên đăng nhập").pack(anchor="w", padx=40)
        self.username_entry = ctk.CTkEntry(frame, width=300)
        self.username_entry.pack(pady=(5, 20))

        ctk.CTkLabel(frame, text="Mật khẩu").pack(anchor="w", padx=40)
        self.password_entry = ctk.CTkEntry(frame, width=300, show="*")
        self.password_entry.pack(pady=(5, 20))
        
        ctk.CTkButton(frame, text="Đăng nhập", width=300, command=self.login).pack(pady=10)
        
        register_frame = ctk.CTkFrame(frame, fg_color="transparent")
        register_frame.pack(pady=20)
        ctk.CTkLabel(register_frame, text="Chưa có tài khoản?").pack(side="left")
        ctk.CTkButton(register_frame, text="Đăng ký", fg_color="transparent", text_color=("gray10", "#DCE4EE"), hover=False, command=self.open_register_screen).pack(side="left")

    def open_register_screen(self):
        """Mở cửa sổ đăng ký."""
        from .register_screen import RegisterScreen
        # Cửa sổ đăng ký sẽ tự quản lý vòng đời của nó
        RegisterScreen(master=self.app, logger_main=self.logger)

    def login(self):
        """Xử lý logic đăng nhập."""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            CTkMessagebox(title="Lỗi", message="Vui lòng nhập đầy đủ thông tin.", icon="cancel")
            return
            
        is_valid, user_info = module_user.check_credentials(username, password)
        
        if is_valid:
            self.app.on_login_success(user_info)
        else:
            CTkMessagebox(title="Lỗi", message="Tên đăng nhập hoặc mật khẩu không chính xác.", icon="cancel")