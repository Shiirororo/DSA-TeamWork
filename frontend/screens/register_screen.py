import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from middleware import module_user

class RegisterScreen(ctk.CTkToplevel):
    def __init__(self, master, logger_main, **kwargs):
        super().__init__(master, **kwargs)
        self.app = master
        self.logger = logger_main
        self.title("Đăng Ký Tài Khoản Mới")
        self.geometry("400x600") # Tăng chiều cao để chứa thêm trường
        self.transient(master)
        self.grab_set()

        # --- Giao diện ---
        frame = ctk.CTkFrame(self)
        frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        ctk.CTkLabel(frame, text="Tạo Tài Khoản", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(10, 20))
        
        ctk.CTkLabel(frame, text="Họ và tên").pack(anchor="w", padx=20)
        self.full_name_entry = ctk.CTkEntry(frame, width=300)
        self.full_name_entry.pack(pady=(5, 15))

        ctk.CTkLabel(frame, text="Tên đăng nhập").pack(anchor="w", padx=20)
        self.username_entry = ctk.CTkEntry(frame, width=300)
        self.username_entry.pack(pady=(5, 15))

        ctk.CTkLabel(frame, text="Email").pack(anchor="w", padx=20)
        self.email_entry = ctk.CTkEntry(frame, width=300)
        self.email_entry.pack(pady=(5, 15))

        ctk.CTkLabel(frame, text="Số điện thoại").pack(anchor="w", padx=20)
        self.phone_entry = ctk.CTkEntry(frame, width=300)
        self.phone_entry.pack(pady=(5, 15))

        ctk.CTkLabel(frame, text="Mật khẩu (ít nhất 6 ký tự)").pack(anchor="w", padx=20)
        self.password_entry = ctk.CTkEntry(frame, width=300, show="*")
        self.password_entry.pack(pady=(5, 15))

        ctk.CTkLabel(frame, text="Xác nhận mật khẩu").pack(anchor="w", padx=20)
        self.confirm_password_entry = ctk.CTkEntry(frame, width=300, show="*")
        self.confirm_password_entry.pack(pady=(5, 15))
        
        ctk.CTkButton(frame, text="Đăng ký", width=300, command=self.submit_registration).pack(pady=20)

    def submit_registration(self):
        full_name = self.full_name_entry.get()
        username = self.username_entry.get()
        email = self.email_entry.get()
        phone = self.phone_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if not all([full_name, username, password, confirm_password, email, phone]):
            CTkMessagebox(master=self, title="Lỗi", message="Vui lòng điền đầy đủ thông tin.", icon="cancel")
            return
        
        if password != confirm_password:
            CTkMessagebox(master=self, title="Lỗi", message="Mật khẩu xác nhận không khớp.", icon="cancel")
            return
        
        self.logger.info(f"Đang gửi yêu cầu đăng ký cho user: {username}")
        
        # [ĐÃ SỬA] Thay đổi thứ tự tham số cho đúng với hàm mới
        success, message = module_user.register_user(full_name, username, password, email, phone)
        
        self.logger.info(f"Kết quả từ middleware: success={success}, message='{message}'")
        
        if success:
            CTkMessagebox(master=self, title="Thành công", message="Đăng ký tài khoản thành công! Vui lòng đăng nhập.", icon="check")
            self.destroy()
        else:
            CTkMessagebox(master=self, title="Lỗi", message=message, icon="cancel")
