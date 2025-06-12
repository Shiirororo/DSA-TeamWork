import customtkinter as ctk
import json
import os
import ctypes

# --- PATH SETUP ---
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
    # Thử đường dẫn cho Windows
    DLL_PATH = os.path.abspath(os.path.join(base_dir, 'cCode', 'lib', 'createProject.dll'))
    c_lib = ctypes.CDLL(DLL_PATH)
except OSError:
    # Thử đường dẫn cho macOS hoặc Linux nếu có
    DLL_PATH = os.path.abspath(os.path.join(base_dir, 'cCode', 'lib', 'createProject.so'))
    c_lib = ctypes.CDLL(DLL_PATH)

MEMBER_FILE_PATH = os.path.join(base_dir, 'data store', 'member.json')
PASSWORD_FILE_PATH = os.path.join(base_dir, 'data store', 'password.json')

# --- HÀM TRỢ GIÚP ĐỌC/GHI FILE (Vẫn giữ để đọc file cho các hàm đơn giản)---
def _read_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content: return []
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# --- [QUAN TRỌNG] KHAI BÁO CÁC HÀM C MỚI ---
def setup_c_signatures():
    global register_user_c, delete_user_c, update_user_role_c, change_password_c

    # int register_user(...)
    register_user_c = c_lib.register_user
    register_user_c.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
    register_user_c.restype = ctypes.c_int

    # int delete_user_by_id_c(...)
    delete_user_c = c_lib.delete_user_by_id_c
    delete_user_c.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
    delete_user_c.restype = ctypes.c_int

    # int update_user_role_c(...)
    update_user_role_c = c_lib.update_user_role_c
    update_user_role_c.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
    update_user_role_c.restype = ctypes.c_int
    
    # int change_password_c(...)
    change_password_c = c_lib.change_password_c
    change_password_c.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
    change_password_c.restype = ctypes.c_int

# Gọi hàm để thiết lập các khai báo
setup_c_signatures()

# --- PYTHON WRAPPER FUNCTIONS (Bỏ logic cũ, gọi C) ---

def get_all_users():
    """Lấy danh sách tất cả người dùng (vẫn dùng Python vì đơn giản)."""
    return _read_json(MEMBER_FILE_PATH)

def check_credentials(username, password):
    """
    Kiểm tra thông tin đăng nhập và hợp nhất thông tin user.
    """
    passwords = _read_json(PASSWORD_FILE_PATH)
    users = _read_json(MEMBER_FILE_PATH)
    
    for cred in passwords:
        if cred.get('username') == username and cred.get('password') == password:
            user_id = cred.get('id')
            # Tìm thông tin chi tiết trong file member.json
            for user_details in users:
                if user_details.get('id') == user_id:
                    # Hợp nhất thông tin từ cả hai file
                    full_user_info = user_details.copy() # Bắt đầu với thông tin từ member.json
                    full_user_info['username'] = cred.get('username') # Thêm username từ password.json
                    
                    # Chuyển đổi vai trò số thành chữ nếu cần
                    if full_user_info.get('role') == 1:
                        full_user_info['role'] = 'Admin'
                    elif full_user_info.get('role') == 0:
                        full_user_info['role'] = 'User'
                        
                    return True, full_user_info
    return False, None

def register_user(name, username, password, email, phone, role="User"):
    """Đăng ký người dùng mới bằng cách gọi hàm C."""
    new_user_id = "USR-" + os.urandom(4).hex()
    result = register_user_c(
        MEMBER_FILE_PATH.encode('utf-8'),
        PASSWORD_FILE_PATH.encode('utf-8'),
        new_user_id.encode('utf-8'),
        name.encode('utf-8'),
        username.encode('utf-8'),
        password.encode('utf-8'),
        email.encode('utf-8'),
        phone.encode('utf-8'),
        role.encode('utf-8')
    )
    if result == 1:
        return True, "Đăng ký thành công!"
    elif result == -1:
        return False, "Tên đăng nhập đã tồn tại."
    elif result == -2:
        return False, "Email đã được sử dụng."
    else:
        return False, "Đã xảy ra lỗi khi đăng ký."

def delete_user(user_id):
    """Xóa người dùng bằng cách gọi hàm C."""
    result = delete_user_c(
        MEMBER_FILE_PATH.encode('utf-8'),
        PASSWORD_FILE_PATH.encode('utf-8'),
        user_id.encode('utf-8')
    )
    return result == 1

def update_user_role(user_id, new_role):
    """Cập nhật vai trò bằng cách gọi hàm C."""
    result = update_user_role_c(
        MEMBER_FILE_PATH.encode('utf-8'),
        user_id.encode('utf-8'),
        new_role.encode('utf-8')
    )
    return result == 1
    
def change_password(user_id, old_password, new_password):
    """Thay đổi mật khẩu bằng cách gọi hàm C."""
    result = change_password_c(
        PASSWORD_FILE_PATH.encode('utf-8'),
        user_id.encode('utf-8'),
        old_password.encode('utf-8'),
        new_password.encode('utf-8')
    )
    if result == 1:
        return True, "Đổi mật khẩu thành công!"
    elif result == -1:
        return False, "Mật khẩu cũ không chính xác."
    elif result == -2:
        return False, "Mật khẩu không được để trống."
    else:
        return False, "Không tìm thấy người dùng hoặc đã xảy ra lỗi."
