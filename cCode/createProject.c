#include <windows.h>
#include "cJSON.h"
#include "implement.h"
#include "validation.h" // Thêm validation header
#include <stdlib.h>

#define DLL_EXPORT __declspec(dllexport)

// =================================================================
// HÀM TIỆN ÍCH (Giữ nguyên)
// =================================================================
// (Các hàm free_c_string, generate_new_project_id, generate_new_task_id không thay đổi)

DLL_EXPORT void free_c_string(char* str) {
    if (str != NULL) {
        free(str);
    }
}

DLL_EXPORT const char* generate_new_project_id(const char* ids_filepath) {
    cJSON* root = read_json_from_file(ids_filepath);
    if (root == NULL) return "PRJ-00000001";
    cJSON* id_json = cJSON_GetObjectItem(root, "project_id");
    int num = atoi(id_json->valuestring + 4);
    num++;
    static char new_id[40];
    sprintf(new_id, "PRJ-%08d", num);
    cJSON_SetValuestring(id_json, new_id);
    write_json_to_file(ids_filepath, root);
    cJSON_Delete(root);
    return new_id;
}


// =================================================================
// CÁC HÀM CRUD CHO PROJECT
// =================================================================

DLL_EXPORT int create_project(const char* filepath, const char* name, const char* description, const char* owner_id, const char* project_id) {
    // --- VALIDATION STEP ---
    if (is_string_empty(name)) {
        return 0; // Không cho phép tên rỗng
    }
    
    cJSON* root = read_json_from_file(filepath);
    if (!root) {
        root = cJSON_CreateArray();
    }
    cJSON* project = cJSON_CreateObject();
    cJSON_AddStringToObject(project, "projectID", project_id);
    cJSON_AddStringToObject(project, "name", name);
    cJSON_AddStringToObject(project, "description", description);
    cJSON_AddStringToObject(project, "ownerID", owner_id);
    cJSON_AddItemToObject(project, "tasks", cJSON_CreateArray());
    cJSON *members = cJSON_CreateArray();
    cJSON *owner_member = cJSON_CreateObject();
    cJSON_AddStringToObject(owner_member, "id", owner_id);
    cJSON_AddItemToArray(members, owner_member);
    cJSON_AddItemToObject(project, "members", members);
    cJSON_AddItemToArray(root, project);
    write_json_to_file(filepath, root);
    cJSON_Delete(root);
    return 1;
}

DLL_EXPORT int delete_project_by_id(const char* filepath, const char* project_id) {
    // --- VALIDATION STEP ---
    if (is_string_empty(project_id)) {
        return 0;
    }

    cJSON* root = read_json_from_file(filepath);
    if (!root) return 0;
    int i = 0;
    cJSON* item;
    cJSON_ArrayForEach(item, root) {
        cJSON* id_json = cJSON_GetObjectItem(item, "projectID");
        if (id_json && cJSON_IsString(id_json) && strcmp(id_json->valuestring, project_id) == 0) {
            cJSON_DeleteItemFromArray(root, i);
            write_json_to_file(filepath, root);
            cJSON_Delete(root);
            return 1;
        }
        i++;
    }
    cJSON_Delete(root);
    return 0;
}

DLL_EXPORT int update_project_by_id(const char* filepath, const char* project_id, const char* new_name, const char* new_description) {
    // --- VALIDATION STEP ---
    if (is_string_empty(project_id) || is_string_empty(new_name)) {
        return 0;
    }
    
    cJSON* root = read_json_from_file(filepath);
    if (!root) return 0;
    cJSON* item;
    int updated = 0;
    cJSON_ArrayForEach(item, root) {
        cJSON* id_json = cJSON_GetObjectItem(item, "projectID");
        if (id_json && cJSON_IsString(id_json) && strcmp(id_json->valuestring, project_id) == 0) {
            cJSON_ReplaceItemInObject(item, "name", cJSON_CreateString(new_name));
            cJSON_ReplaceItemInObject(item, "description", cJSON_CreateString(new_description));
            updated = 1;
            break;
        }
    }
    if (updated) {
        write_json_to_file(filepath, root);
    }
    cJSON_Delete(root);
    return updated;
}


// =================================================================
// CÁC HÀM CRUD CHO TASK
// =================================================================

DLL_EXPORT int add_task_to_project(const char* filepath, const char* project_id, const char* task_id, const char* title, const char* description, const char* assigneeID) {
    // --- VALIDATION STEP ---
    if (is_string_empty(project_id) || is_string_empty(task_id) || is_string_empty(title)) {
        return 0;
    }

    cJSON* root = read_json_from_file(filepath);
    if (!root) return 0;
    cJSON* p_item;
    int updated = 0;
    cJSON_ArrayForEach(p_item, root) {
        cJSON* id_json = cJSON_GetObjectItem(p_item, "projectID");
        if (id_json && cJSON_IsString(id_json) && strcmp(id_json->valuestring, project_id) == 0) {
            cJSON* tasks = cJSON_GetObjectItem(p_item, "tasks");
            if (!tasks) {
                tasks = cJSON_CreateArray();
                cJSON_AddItemToObject(p_item, "tasks", tasks);
            }
            cJSON* new_task = cJSON_CreateObject();
            cJSON_AddStringToObject(new_task, "taskID", task_id);
            cJSON_AddStringToObject(new_task, "title", title);
            cJSON_AddStringToObject(new_task, "description", description);
            cJSON_AddStringToObject(new_task, "status", "Todo");
            cJSON_AddStringToObject(new_task, "assigneeID", assigneeID);
            cJSON_AddItemToArray(tasks, new_task);
            updated = 1;
            break;
        }
    }
    if (updated) {
        write_json_to_file(filepath, root);
    }
    cJSON_Delete(root);
    return updated;
}

DLL_EXPORT int update_task_status(const char* filepath, const char* project_id, const char* task_id, const char* new_status) {
    // --- VALIDATION STEP ---
    if (is_string_empty(project_id) || is_string_empty(task_id) || !is_valid_status(new_status)) {
        return 0;
    }

    cJSON* root = read_json_from_file(filepath);
    if (!root) return 0;
    cJSON* p_item;
    int updated = 0;
    cJSON_ArrayForEach(p_item, root) {
        cJSON* p_id_json = cJSON_GetObjectItem(p_item, "projectID");
        if (p_id_json && cJSON_IsString(p_id_json) && strcmp(p_id_json->valuestring, project_id) == 0) {
            cJSON* tasks = cJSON_GetObjectItem(p_item, "tasks");
            cJSON* t_item;
            cJSON_ArrayForEach(t_item, tasks) {
                cJSON* t_id_json = cJSON_GetObjectItem(t_item, "taskID");
                if (t_id_json && cJSON_IsString(t_id_json) && strcmp(t_id_json->valuestring, task_id) == 0) {
                    cJSON_ReplaceItemInObject(t_item, "status", cJSON_CreateString(new_status));
                    updated = 1;
                    break;
                }
            }
            if (updated) break;
        }
    }
    if (updated) {
        write_json_to_file(filepath, root);
    }
    cJSON_Delete(root);
    return updated;
}

DLL_EXPORT int delete_task_from_project(const char* filepath, const char* project_id, const char* task_id) {
    // --- VALIDATION STEP ---
    if (is_string_empty(project_id) || is_string_empty(task_id)) {
        return 0;
    }

    cJSON* root = read_json_from_file(filepath);
    if (!root) return 0;
    int updated = 0;
    cJSON* p_item;
    cJSON_ArrayForEach(p_item, root) {
        cJSON* p_id_json = cJSON_GetObjectItem(p_item, "projectID");
        if (p_id_json && cJSON_IsString(p_id_json) && strcmp(p_id_json->valuestring, project_id) == 0) {
            cJSON* tasks = cJSON_GetObjectItem(p_item, "tasks");
            int i = 0;
            cJSON* t_item;
            cJSON_ArrayForEach(t_item, tasks) {
                cJSON* t_id_json = cJSON_GetObjectItem(t_item, "taskID");
                if (t_id_json && cJSON_IsString(t_id_json) && strcmp(t_id_json->valuestring, task_id) == 0) {
                    cJSON_DeleteItemFromArray(tasks, i);
                    updated = 1;
                    break;
                }
                i++;
            }
            if (updated) break;
        }
    }
    if (updated) {
        write_json_to_file(filepath, root);
    }
    cJSON_Delete(root);
    return updated;
}


// =================================================================
// CÁC HÀM CRUD CHO MEMBER
// =================================================================

DLL_EXPORT int add_member_to_project(const char* filepath, const char* projectID, const char* memberID) {
    // --- VALIDATION STEP ---
    if (is_string_empty(projectID) || is_string_empty(memberID)) {
        return 0;
    }

    cJSON *root = read_json_from_file(filepath);
    if (!root) return 0;
    int updated = 0;
    cJSON *p_item;
    cJSON_ArrayForEach(p_item, root) {
        cJSON* id_json = cJSON_GetObjectItem(p_item, "projectID");
        if (id_json && cJSON_IsString(id_json) && strcmp(id_json->valuestring, projectID) == 0) {
            cJSON *members = cJSON_GetObjectItem(p_item, "members");
            if (!cJSON_IsArray(members)) break;
            int exists = 0;
            cJSON *m_item;
            cJSON_ArrayForEach(m_item, members) {
                cJSON* member_id_json = cJSON_GetObjectItem(m_item, "id");
                if (member_id_json && cJSON_IsString(member_id_json) && strcmp(member_id_json->valuestring, memberID) == 0) {
                    exists = 1;
                    break;
                }
            }
            if (!exists) {
                cJSON *new_member = cJSON_CreateObject();
                cJSON_AddStringToObject(new_member, "id", memberID);
                cJSON_AddItemToArray(members, new_member);
                updated = 1;
            }
            break;
        }
    }
    if (updated) {
        write_json_to_file(filepath, root);
    }
    cJSON_Delete(root);
    return updated;
}

DLL_EXPORT int remove_member_from_project(const char* filepath, const char* projectID, const char* memberID) {
    // --- VALIDATION STEP ---
    if (is_string_empty(projectID) || is_string_empty(memberID)) {
        return 0;
    }

    cJSON *root = read_json_from_file(filepath);
    if (!root) return 0;
    int removed = 0;
    cJSON *p_item;
    cJSON_ArrayForEach(p_item, root) {
        cJSON* id_json = cJSON_GetObjectItem(p_item, "projectID");
        if (id_json && cJSON_IsString(id_json) && strcmp(id_json->valuestring, projectID) == 0) {
            cJSON *members = cJSON_GetObjectItem(p_item, "members");
            if (!cJSON_IsArray(members)) break;
            int member_index = -1, current_index = 0;
            cJSON *m_item;
            cJSON_ArrayForEach(m_item, members) {
                cJSON* member_id_json = cJSON_GetObjectItem(m_item, "id");
                 if (member_id_json && cJSON_IsString(member_id_json) && strcmp(member_id_json->valuestring, memberID) == 0) {
                    member_index = current_index;
                    break;
                }
                current_index++;
            }
            if (member_index != -1) {
                cJSON_DeleteItemFromArray(members, member_index);
                removed = 1;
            }
            break;
        }
    }
    if (removed) {
        write_json_to_file(filepath, root);
    }
    cJSON_Delete(root);
    return removed;
}

DLL_EXPORT int assign_task_to_member(const char* filepath, const char* projectID, const char* taskID, const char* assigneeID) {
    // --- VALIDATION STEP ---
    if (is_string_empty(projectID) || is_string_empty(taskID)) {
        return 0;
    }

    cJSON *root = read_json_from_file(filepath);
    if (!root) return 0;
    int updated = 0;
    cJSON *p_item;
    cJSON_ArrayForEach(p_item, root) {
        cJSON* p_id_json = cJSON_GetObjectItem(p_item, "projectID");
        if (p_id_json && cJSON_IsString(p_id_json) && strcmp(p_id_json->valuestring, projectID) == 0) {
            cJSON *tasks = cJSON_GetObjectItem(p_item, "tasks");
            cJSON *t_item;
            cJSON_ArrayForEach(t_item, tasks) {
                cJSON* t_id_json = cJSON_GetObjectItem(t_item, "taskID");
                if (t_id_json && cJSON_IsString(t_id_json) && strcmp(t_id_json->valuestring, taskID) == 0) {
                    // Chú ý: assigneeID có thể rỗng (un-assign) nên không cần check is_string_empty
                    cJSON_ReplaceItemInObject(t_item, "assigneeID", cJSON_CreateString(assigneeID));
                    updated = 1;
                    break;
                }
            }
            if(updated) break;
        }
    }
    if (updated) {
        write_json_to_file(filepath, root);
    }
    cJSON_Delete(root);
    return updated;
}