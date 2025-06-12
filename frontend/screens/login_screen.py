import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from middleware import module_user
from PIL import Image
import os # Import os để làm việc với đường dẫn file

class LoginPage(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master)
        self.app = app
        self.logger = app.logger

        # --- Cấu hình layout chính ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # =================================================================
        # KHUNG BÊN TRÁI (TRANG TRÍ)
        # =================================================================
        self.left_frame = ctk.CTkFrame(self, fg_color=("#F0F0F0", "#202020"), corner_radius=0)
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)

        # --- Tải ảnh nền và thiết lập sự kiện resize ---
        try:
            image_path = os.path.join("frontend", "screens", "images", "login_bg.png")
            self.bg_image_data = Image.open(image_path)
            
            self.bg_label = ctk.CTkLabel(self.left_frame, text="")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

            # Gắn sự kiện <Configure> để tự động thay đổi kích thước ảnh
            self.left_frame.bind("<Configure>", self.resize_bg_image)

            # Thêm lớp phủ mờ để chữ nổi bật hơn
            overlay = ctk.CTkFrame(self.left_frame, fg_color=("#000000"), bg_color="transparent", corner_radius=0)
            overlay.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)
            overlay.lower()
            
            # Thêm tiêu đề và slogan
            title_label = ctk.CTkLabel(overlay, text="ProjectFlow", font=ctk.CTkFont(size=40, weight="bold"), text_color="white")
            title_label.place(relx=0.5, rely=0.45, anchor="center")
            slogan_label = ctk.CTkLabel(overlay, text="Your Ideas, Seamlessly Managed.", font=ctk.CTkFont(size=16), text_color="white")
            slogan_label.place(relx=0.5, rely=0.5, anchor="center")

        except FileNotFoundError:
            self.logger.error(f"Không tìm thấy ảnh nền tại: {image_path}")
            ctk.CTkLabel(self.left_frame, text="Project Management Tool", font=ctk.CTkFont(size=30)).place(relx=0.5, rely=0.5, anchor="center")
        except Exception as e:
            self.logger.error(f"Lỗi xử lý ảnh nền: {e}")

        # =================================================================
        # KHUNG BÊN PHẢI (FORM ĐĂNG NHẬP)
        # =================================================================
        self.right_frame = ctk.CTkFrame(self, fg_color=("#FFFFFF", "#2B2B2B"), corner_radius=0)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)
        
        form_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        form_frame.grid(row=0, column=0) # Canh giữa form

        # --- Tải icon cho các ô nhập liệu ---
        try:
            self.mail_icon = ctk.CTkImage(Image.open("frontend/screens/images/mail.png"), size=(20, 20))
            self.lock_icon = ctk.CTkImage(Image.open("frontend/screens/images/lock.png"), size=(20, 20))
        except FileNotFoundError:
            self.logger.error(f"Không tìm thấy file icon mail.png hoặc lock.png")
            self.mail_icon, self.lock_icon = None, None

        ctk.CTkLabel(form_frame, text="Đăng Nhập", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=(0, 30))
        
        # --- Khung Tên đăng nhập ---
        username_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        username_frame.pack(pady=10, fill="x")
        if self.mail_icon: ctk.CTkLabel(username_frame, image=self.mail_icon, text="").pack(side="left", padx=(0, 10))
        self.username_entry = ctk.CTkEntry(username_frame, width=300, height=40, placeholder_text="Tên đăng nhập", corner_radius=8)
        self.username_entry.pack(side="left", fill="x", expand=True)

        # --- Khung Mật khẩu ---
        password_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        password_frame.pack(pady=10, fill="x")
        if self.lock_icon: ctk.CTkLabel(password_frame, image=self.lock_icon, text="").pack(side="left", padx=(0, 10))
        self.password_entry = ctk.CTkEntry(password_frame, width=300, height=40, show="*", placeholder_text="Mật khẩu", corner_radius=8)
        self.password_entry.pack(side="left", fill="x", expand=True)
        
        # --- Checkbox Hiển thị mật khẩu ---
        self.show_password_var = ctk.StringVar(value="off")
        show_password_checkbox = ctk.CTkCheckBox(form_frame, text="Hiển thị mật khẩu", variable=self.show_password_var, onvalue="on", offvalue="off", command=self.toggle_password_visibility)
        show_password_checkbox.pack(padx=5, pady=10, anchor="w")

        # --- Nút Đăng nhập ---
        ctk.CTkButton(form_frame, text="Đăng nhập", width=300, height=40, command=self.login, corner_radius=8, font=ctk.CTkFont(weight="bold")).pack(pady=(20, 15))
        
        # --- Link Đăng ký ---
        register_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        register_frame.pack(pady=10)
        ctk.CTkLabel(register_frame, text="Chưa có tài khoản?").pack(side="left")
        ctk.CTkButton(register_frame, text="Đăng ký ngay", fg_color="transparent", text_color=("#3B8ED0", "#DCE4EE"), hover=False, command=self.open_register_screen).pack(side="left")

    def _resize_and_crop(self, image, target_width, target_height):
        """
        [MỚI] Hàm trợ giúp để resize và crop ảnh giữ nguyên tỉ lệ.
        """
        img_width, img_height = image.size
        img_ratio = img_width / float(img_height)
        target_ratio = target_width / float(target_height)

        if target_ratio > img_ratio:
            # Khung chứa rộng hơn ảnh -> scale theo chiều rộng
            scaled_width = target_width
            scaled_height = int(target_width / img_ratio)
        else:
            # Khung chứa cao hơn ảnh -> scale theo chiều cao
            scaled_height = target_height
            scaled_width = int(target_height * img_ratio)

        resized_image = image.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)

        # Crop ảnh từ tâm
        x_offset = (scaled_width - target_width) / 2
        y_offset = (scaled_height - target_height) / 2
        
        cropped_image = resized_image.crop((x_offset, y_offset, x_offset + target_width, y_offset + target_height))
        
        return cropped_image

    def resize_bg_image(self, event):
        """
        [CẬP NHẬT] Hàm được gọi mỗi khi khung bên trái thay đổi kích thước.
        """
        new_width = event.width
        new_height = event.height
        
        if new_width <= 1 or new_height <= 1:
            return # Bỏ qua nếu kích thước không hợp lệ

        # Sử dụng hàm trợ giúp để có ảnh đã được crop hoàn hảo
        cropped_image = self._resize_and_crop(self.bg_image_data, new_width, new_height)
        
        # Tạo ảnh mới với kích thước của khung
        bg_image = ctk.CTkImage(light_image=cropped_image, dark_image=cropped_image, size=(new_width, new_height))
        
        # Cập nhật ảnh cho label
        self.bg_label.configure(image=bg_image)


    def toggle_password_visibility(self):
        self.password_entry.configure(show="" if self.show_password_var.get() == "on" else "*")

    def open_register_screen(self):
        from .register_screen import RegisterScreen
        RegisterScreen(master=self.app, logger_main=self.logger)

    def login(self):
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
