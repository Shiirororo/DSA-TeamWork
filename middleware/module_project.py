import ctypes
import json
import os
import uuid
from .log import log_setting

logger = log_setting(__name__)

# --- PATH SETUP ---
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Sửa lại đường dẫn DLL cho chính xác
DLL_PATH = os.path.abspath(os.path.join(base_dir, 'cCode', 'lib', 'createProject.dll'))
PROJECTS_FILE_PATH = os.path.join(base_dir, 'data store', 'project.json')

# --- LOAD C LIBRARY ---
try:
    c_lib = ctypes.CDLL(DLL_PATH)
except OSError as e:
    logger.critical(f"FATAL: Could not load C library from {DLL_PATH}. Error: {e}")
    # Có thể thêm xử lý thoát chương trình ở đây nếu DLL là bắt buộc
    exit()

# --- DEFINE C FUNCTION SIGNATURES ---
def setup_c_signatures():
    global free_c_string, create_project_c, delete_project_c, update_project_c
    global add_task_c, update_task_status_c, delete_task_c, add_member_c, remove_member_c, assign_task_c

    free_c_string = c_lib.free_c_string
    free_c_string.argtypes = [ctypes.c_char_p]
    free_c_string.restype = None

    create_project_c = c_lib.create_project
    create_project_c.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
    create_project_c.restype = ctypes.c_int

    delete_project_c = c_lib.delete_project_by_id
    delete_project_c.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    delete_project_c.restype = ctypes.c_int

    update_project_c = c_lib.update_project_by_id
    update_project_c.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
    update_project_c.restype = ctypes.c_int
    
    add_task_c = c_lib.add_task_to_project
    add_task_c.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
    add_task_c.restype = ctypes.c_int

    update_task_status_c = c_lib.update_task_status
    update_task_status_c.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
    update_task_status_c.restype = ctypes.c_int

    delete_task_c = c_lib.delete_task_from_project
    delete_task_c.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
    delete_task_c.restype = ctypes.c_int

    add_member_c = c_lib.add_member_to_project
    add_member_c.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
    add_member_c.restype = ctypes.c_int

    remove_member_c = c_lib.remove_member_from_project
    remove_member_c.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
    remove_member_c.restype = ctypes.c_int
    
    assign_task_c = c_lib.assign_task_to_member
    assign_task_c.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
    assign_task_c.restype = ctypes.c_int

setup_c_signatures()

# --- PYTHON WRAPPER FUNCTIONS ---
def get_all_projects():
    try:
        with open(PROJECTS_FILE_PATH, "r", encoding='utf-8') as f:
            content = f.read()
            # Tránh lỗi nếu file rỗng
            if not content.strip():
                return []
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error reading or parsing project.json: {e}")
        return []

def get_project_by_id(project_id):
    all_projects = get_all_projects()
    for project in all_projects:
        if project.get('projectID') == project_id:
            return project
    return None

def create_project(name, description, owner_id):
    project_id = "PRJ-" + str(uuid.uuid4())
    result = create_project_c(
        PROJECTS_FILE_PATH.encode('utf-8'),
        name.encode('utf-8'),
        description.encode('utf-8'),
        owner_id.encode('utf-8'),
        project_id.encode('utf-8')
    )
    return project_id if result == 1 else None

def delete_project(project_id):
    return delete_project_c(PROJECTS_FILE_PATH.encode('utf-8'), project_id.encode('utf-8')) == 1

def update_project(project_id, new_name, new_description):
    return update_project_c(PROJECTS_FILE_PATH.encode('utf-8'), project_id.encode('utf-8'), new_name.encode('utf-8'), new_description.encode('utf-8')) == 1

def add_task(project_id, title, description, assignee_id=""):
    task_id = "TSK-" + str(uuid.uuid4())
    return add_task_c(
        PROJECTS_FILE_PATH.encode('utf-8'),
        project_id.encode('utf-8'),
        task_id.encode('utf-8'),
        title.encode('utf-8'),
        description.encode('utf-8'),
        assignee_id.encode('utf-8')
    ) == 1

def update_task_status(project_id, task_id, new_status):
    return update_task_status_c(PROJECTS_FILE_PATH.encode('utf-8'), project_id.encode('utf-8'), task_id.encode('utf-8'), new_status.encode('utf-8')) == 1

def delete_task(project_id, task_id):
    return delete_task_c(PROJECTS_FILE_PATH.encode('utf-8'), project_id.encode('utf-8'), task_id.encode('utf-8')) == 1

def add_member_to_project(project_id, member_id):
    return add_member_c(PROJECTS_FILE_PATH.encode('utf-8'), project_id.encode('utf-8'), member_id.encode('utf-8')) == 1

def remove_member_from_project(project_id, member_id):
    return remove_member_c(PROJECTS_FILE_PATH.encode('utf-8'), project_id.encode('utf-8'), member_id.encode('utf-8')) == 1
    
def assign_task(project_id, task_id, assignee_id):
    return assign_task_c(
        PROJECTS_FILE_PATH.encode('utf-8'),
        project_id.encode('utf-8'),
        task_id.encode('utf-8'),
        assignee_id.encode('utf-8')
    ) == 1