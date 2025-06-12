import json
import uuid
import os
from .log import log_setting

logger = log_setting(__name__)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMBER_FILE = os.path.join(base_dir, 'data store', 'member.json')
PASSWORD_FILE = os.path.join(base_dir, 'data store', 'password.json')

def _read_json_file(file_path):
    """Hàm nội bộ để đọc file JSON một cách an toàn."""
    try:
        if not os.path.exists(file_path): return []
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def _write_json_file(file_path, data):
    """Hàm nội bộ để ghi file JSON."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def check_credentials(username, password):
    """
    Kiểm tra thông tin đăng nhập từ file password.json và lấy thông tin chi tiết
    từ member.json. Trả về (True, user_info_dict) hoặc (False, None).
    """
    logger.debug(f"Đang kiểm tra đăng nhập cho user: {username}")
    passwords = _read_json_file(PASSWORD_FILE)
    members = _read_json_file(MEMBER_FILE)
    
    user_id = next((user.get('id') for user in passwords if user.get('username') == username and user.get('password') == password), None)
            
    if user_id:
        user_info = next((member for member in members if member.get('id') == user_id), None)
        if user_info:
            logger.info(f"Đăng nhập thành công cho user: {username}")
            return True, user_info
    
    logger.warning(f"Đăng nhập thất bại cho user: {username}")
    return False, None

def register_user(username, password, name, email, phone):
    """Đăng ký người dùng mới."""
    passwords = _read_json_file(PASSWORD_FILE)
    if any(user.get('username') == username for user in passwords):
        return False, "Tên đăng nhập đã tồn tại"
    
    new_user_id = "USR-" + str(uuid.uuid4())
    new_password_entry = {"username": username, "password": password, "id": new_user_id}
    passwords.append(new_password_entry)
    _write_json_file(PASSWORD_FILE, passwords)
    
    members = _read_json_file(MEMBER_FILE)
    new_member_entry = {"id": new_user_id, "name": name, "role": "Member", "email": email, "phone": phone}
    members.append(new_member_entry)
    _write_json_file(MEMBER_FILE, members)
    
    return True, "Đăng ký thành công"

def get_all_users():
    """Lấy tất cả người dùng."""
    return _read_json_file(MEMBER_FILE)

def update_user_role(user_id, new_role):
    """Cập nhật vai trò người dùng."""
    members = _read_json_file(MEMBER_FILE)
    user_found = False
    for user in members:
        if user.get('id') == user_id:
            user['role'] = new_role
            user_found = True
            break
    if user_found:
        _write_json_file(MEMBER_FILE, members)
        return True
    return False

def delete_user(user_id):
    """Xóa người dùng khỏi cả 2 file member và password."""
    members = _read_json_file(MEMBER_FILE)
    passwords = _read_json_file(PASSWORD_FILE)
    
    new_members = [user for user in members if user.get('id') != user_id]
    
    if len(new_members) < len(members):
        new_passwords = [p for p in passwords if p.get('id') != user_id]
        _write_json_file(MEMBER_FILE, new_members)
        _write_json_file(PASSWORD_FILE, new_passwords)
        return True
    return False