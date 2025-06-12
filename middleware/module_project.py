import ctypes
import json
import os
from .log import log_setting

logger = log_setting(__name__)

# --- Định nghĩa các đường dẫn tuyệt đối ---
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DLL_PATH = os.path.abspath(os.path.join(base_dir, 'cCode', 'lib', 'createProject.dll'))
PROJECTS_FILE_PATH = os.path.join(base_dir, 'data store', 'project.json')
IDS_FILE_PATH = os.path.join(base_dir, 'data store', 'latest_ids.json')

c_lib = ctypes.CDLL(DLL_PATH)


# --- Định nghĩa các hàm C ---
free_c_string = c_lib.free_c_string
free_c_string.argtypes = [ctypes.c_void_p]
free_c_string.restype = None

create_project_c = c_lib.create_project
create_project_c.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
create_project_c.restype = ctypes.c_int

delete_project_c = c_lib.delete_project_by_id
delete_project_c.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
delete_project_c.restype = ctypes.c_int

update_project_c = c_lib.update_project_by_id
update_project_c.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
update_project_c.restype = ctypes.c_int

add_task_to_project_c = c_lib.add_task_to_project
add_task_to_project_c.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
add_task_to_project_c.restype = ctypes.c_int

assign_task_c = c_lib.assign_task_to_member
assign_task_c.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
assign_task_c.restype = ctypes.c_int

add_task_c = c_lib.add_task_to_project
add_task_c.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
add_task_c.restype = ctypes.c_int

update_task_status_c = c_lib.update_task_status
update_task_status_c.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
update_task_status_c.restype = ctypes.c_int


delete_task_c = c_lib.delete_task_from_project
delete_task_c.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
delete_task_c.restype = ctypes.c_int

# Định nghĩa hàm add_member_to_project từ C
add_member_c = c_lib.add_member_to_project
add_member_c.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
add_member_c.restype = ctypes.c_int

# Định nghĩa hàm remove_member_from_project từ C
remove_member_c = c_lib.remove_member_from_project
remove_member_c.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
remove_member_c.restype = ctypes.c_int


# --- Các hàm Python wrapper ---

def get_next_id(id_prefix: str, id_key: str) -> str:
    """Hàm tạo ID mới, viết hoàn toàn bằng Python."""
    try:
        with open(IDS_FILE_PATH, 'r+') as f:
            ids_data = json.load(f)
            current_id = ids_data.get(id_key, 0)
            next_id_val = current_id + 1
            ids_data[id_key] = next_id_val
            f.seek(0)
            json.dump(ids_data, f, indent=4)
            f.truncate()
            return f"{id_prefix}{next_id_val:09d}"
    except (FileNotFoundError, json.JSONDecodeError):
        with open(IDS_FILE_PATH, 'w') as f:
            ids_data = { "project": 0, "task": 0 }
            ids_data[id_key] = 1
            json.dump(ids_data, f, indent=4)
            return f"{id_prefix}{1:09d}"
    except Exception as e:
        logger.error(f"Lỗi không xác định trong get_next_id: {e}")
        return ""

def get_all_projects():
    """Đọc trực tiếp từ Python để lấy danh sách dự án."""
    try:
        if not os.path.exists(PROJECTS_FILE_PATH): return []
        with open(PROJECTS_FILE_PATH, "r", encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Lỗi khi đọc project.json: {e}")
        return []

def get_project_by_id(project_id):
    """
    Lọc và trả về dữ liệu của một dự án duy nhất bằng ID của nó.
    
    Args:
        project_id (str): ID của dự án cần tìm.

    Returns:
        dict: Dữ liệu của dự án nếu tìm thấy, ngược lại trả về None.
    """
    all_projects = get_all_projects()
    for project in all_projects:
        if project.get('projectID') == project_id:
            return project
    return None # Trả về None nếu không tìm thấy dự án


def create_project(name, description, owner_id):
    """Tạo ID bằng Python, sau đó gọi C để ghi vào file."""
    project_id = get_next_id("PRJ", "project")
    if not project_id: return False
    result = create_project_c(PROJECTS_FILE_PATH.encode('utf-8'), project_id.encode('utf-8'), name.encode('utf-8'), description.encode('utf-8'), owner_id.encode('utf-8'))
    return result == 1

def delete_project(project_id):
    return delete_project_c(PROJECTS_FILE_PATH.encode('utf-8'), project_id.encode('utf-8')) == 1

def update_project(project_id, new_name, new_description):
    return update_project_c(PROJECTS_FILE_PATH.encode('utf-8'), project_id.encode('utf-8'), new_name.encode('utf-8'), new_description.encode('utf-8')) == 1

import uuid
def add_task(project_id, title, description, assignee_id=""): # Thêm assignee_id
    """
    Wrapper Python để gọi hàm C thêm task vào dự án.
    """
    task_id = "TSK-" + str(uuid.uuid4())
    logger.debug(f"Yêu cầu thêm task '{title}' vào project '{project_id}'")
    
    # Truyền assignee_id vào hàm C
    result = add_task_to_project_c(
        PROJECTS_FILE_PATH.encode('utf-8'),
        project_id.encode('utf-8'),
        task_id.encode('utf-8'),
        title.encode('utf-8'),
        description.encode('utf-8'),
        assignee_id.encode('utf-8')
    )
    
    if result == 1:
        logger.info(f"Thêm task thành công vào project '{project_id}'")
        return True
    else:
        logger.warning(f"Thêm task vào project '{project_id}' thất bại")
        return False


def update_task_status(project_id, task_id, new_status):
    return update_task_status_c(PROJECTS_FILE_PATH.encode('utf-8'), project_id.encode('utf-8'), task_id.encode('utf-8'), new_status.encode('utf-8')) == 1


def delete_task(project_id, task_id):
    """Gọi C để xóa một task cụ thể khỏi dự án."""
    return delete_task_c(PROJECTS_FILE_PATH.encode('utf-8'), project_id.encode('utf-8'), task_id.encode('utf-8')) == 1

def add_member_to_project(project_id, member_id):
    """
    Wrapper Python để gọi hàm C thêm thành viên vào dự án.
    Trả về True nếu thành công, False nếu thất bại.
    """
    logger.debug(f"Yêu cầu thêm member '{member_id}' vào project '{project_id}'")
    result = add_member_c(PROJECTS_FILE_PATH.encode('utf-8'), project_id.encode('utf-8'), member_id.encode('utf-8'))
    if result == 1:
        logger.info(f"Đã thêm thành công member '{member_id}' vào project '{project_id}'")
        return True
    else:
        logger.warning(f"Thêm member '{member_id}' vào project '{project_id}' thất bại")
        return False

def remove_member_from_project(project_id, member_id):
    """
    Wrapper Python để gọi hàm C xóa thành viên khỏi dự án.
    Trả về True nếu thành công, False nếu thất bại.
    """
    logger.debug(f"Yêu cầu xóa member '{member_id}' khỏi project '{project_id}'")
    result = remove_member_c(PROJECTS_FILE_PATH.encode('utf-8'), project_id.encode('utf-8'), member_id.encode('utf-8'))
    if result == 1:
        logger.info(f"Đã xóa thành công member '{member_id}' khỏi project '{project_id}'")
        return True
    else:
        logger.warning(f"Xóa member '{member_id}' khỏi project '{project_id}' thất bại")
        return False


def assign_task(project_id, task_id, assignee_id):
    """
    Wrapper Python để gọi hàm C gán task cho thành viên.
    """
    logger.debug(f"Yêu cầu gán task '{task_id}' cho member '{assignee_id}' trong project '{project_id}'")
    
    result = assign_task_c(
        PROJECTS_FILE_PATH.encode('utf-8'),
        project_id.encode('utf-8'),
        task_id.encode('utf-8'),
        assignee_id.encode('utf-8')
    )
    
    if result == 1:
        logger.info(f"Gán task '{task_id}' thành công")
        return True
    else:
        logger.warning(f"Gán task '{task_id}' thất bại")
        return False