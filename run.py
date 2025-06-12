import customtkinter as ctk
from middleware.log import log_setting
from frontend.screens.login_screen import LoginPage
from frontend.screens.main_screen import MainScreen, AdminScreen
from frontend.screens.project_detail_screen import ProjectDetailScreen
# from frontend.screens.user_management_screen import UserManagementScreen # [ĐÃ XÓA]
from frontend.screens.profile_screen import ProfileScreen

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.logger = log_setting(__name__)
        self.title("Project Management Tool")
        self.geometry("1100x720")
        try:
            self.iconbitmap("frontend/screens/images/logo.ico")
        except Exception as e:
            self.logger.warning(f"Could not load icon: {e}")

        self._current_frame = None
        self.user_info = None
        self.show_frame(LoginPage)

    def show_frame(self, frame_class, **kwargs):
        """Hàm chung để chuyển đổi giữa các màn hình một cách an toàn."""
        self.logger.debug(f"Yêu cầu chuyển đến màn hình: {frame_class.__name__}")
        if self._current_frame:
            self._current_frame.destroy()
        
        self._current_frame = frame_class(master=self, app=self, **kwargs)
        self.logger.debug(f"Đã tạo instance của {frame_class.__name__}")
        self._current_frame.pack(fill="both", expand=True)

    def on_login_success(self, user_info):
        """Lưu thông tin người dùng và hiển thị màn hình chính."""
        self.logger.info(f"Đăng nhập thành công cho user: {user_info.get('name')}")
        self.user_info = user_info
        self.show_main_menu()

    def show_main_menu(self):
        """Hiển thị màn hình chính (MainScreen hoặc AdminScreen) dựa trên vai trò."""
        if self.user_info and self.user_info.get("role") in ["Admin", "Super Admin"]:
            self.show_frame(AdminScreen, user_info=self.user_info)
        else:
            self.show_frame(MainScreen, user_info=self.user_info)
        
    def show_project_detail_screen(self, project_id):
        """Hiển thị màn hình chi tiết dự án."""
        self.show_frame(ProjectDetailScreen, user_info=self.user_info, project_id=project_id)
        
    # --- [ĐÃ XÓA] Hàm hiển thị màn hình quản lý người dùng ---
    # def show_user_management_screen(self):
    #     self.show_frame(UserManagementScreen, user_info=self.user_info)

    def show_profile_screen(self):
        """Hiển thị màn hình thông tin cá nhân."""
        self.show_frame(ProfileScreen)

    def logout(self):
        """Đăng xuất và quay về màn hình đăng nhập."""
        if self.user_info:
            self.logger.info(f"Người dùng {self.user_info.get('name')} đã đăng xuất.")
        self.user_info = None
        self.show_frame(LoginPage)

if __name__ == "__main__":
    app = App()
    app.mainloop()
