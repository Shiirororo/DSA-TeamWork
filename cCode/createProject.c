// File: cCode/createProject.c (Phiên bản cuối cùng, đã sửa lỗi Access Violation)

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cJSON.h"
#include "struct.h"

// Hàm đọc file JSON (giữ nguyên)
cJSON* read_json_from_file(const char* filepath) {
    FILE* file = fopen(filepath, "rb");
    if (!file) {
        printf("Cannot open file %s\n", filepath);
        return NULL;
    }
    fseek(file, 0, SEEK_END);
    long length = ftell(file);
    fseek(file, 0, SEEK_SET);
    char* content = (char*)malloc(length + 1);
    fread(content, 1, length, file);
    fclose(file);
    content[length] = '\0';
    cJSON* json = cJSON_Parse(content);
    free(content);
    return json;
}

// Hàm ghi file JSON (giữ nguyên)
void write_json_to_file(const char* filepath, cJSON* json) {
    char* out = cJSON_Print(json);
    FILE* file = fopen(filepath, "w");
    if (file) {
        fprintf(file, "%s", out);
        fclose(file);
    }
    free(out);
}

// Các hàm được export ra DLL (ĐÃ SỬA LỖI)

__declspec(dllexport) void free_c_string(char* str) {
    free(str);
}

__declspec(dllexport) int create_project(const char* filepath, const char* name, const char* description, const char* owner_id, const char* project_id, const char* owner_name) {
    cJSON* root = read_json_from_file(filepath);
    if (!root) {
        root = cJSON_CreateArray();
    }
    cJSON* project = cJSON_CreateObject();
    cJSON_AddStringToObject(project, "projectID", project_id);
    cJSON_AddStringToObject(project, "name", name);
    cJSON_AddStringToObject(project, "description", description);
    cJSON_AddStringToObject(project, "ownerID", owner_id);
    cJSON_AddStringToObject(project, "ownerName", owner_name);
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

__declspec(dllexport) int delete_project_by_id(const char* filepath, const char* project_id) {
    cJSON* root = read_json_from_file(filepath);
    if (!root) return 0;
    int i = 0;
    cJSON* item;
    cJSON_ArrayForEach(item, root) {
        cJSON* id_json = cJSON_GetObjectItem(item, "projectID");
        // SỬA LỖI: Kiểm tra NULL trước khi sử dụng
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

__declspec(dllexport) int update_project_by_id(const char* filepath, const char* project_id, const char* new_name, const char* new_description) {
    cJSON* root = read_json_from_file(filepath);
    if (!root) return 0;
    cJSON* item;
    int updated = 0;
    cJSON_ArrayForEach(item, root) {
        cJSON* id_json = cJSON_GetObjectItem(item, "projectID");
        // SỬA LỖI: Kiểm tra NULL trước khi sử dụng
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

__declspec(dllexport) int add_task_to_project(const char* filepath, const char* project_id, const char* task_id, const char* title, const char* description, const char* assigneeID) {
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
            // SỬ DỤNG assigneeID được truyền vào
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

__declspec(dllexport) int update_task_status(const char* filepath, const char* project_id, const char* task_id, const char* new_status) {
    cJSON* root = read_json_from_file(filepath);
    if (!root) return 0;
    cJSON* p_item;
    int updated = 0;
    cJSON_ArrayForEach(p_item, root) {
        cJSON* p_id_json = cJSON_GetObjectItem(p_item, "projectID");
        // SỬA LỖI: Kiểm tra NULL trước khi sử dụng
        if (p_id_json && cJSON_IsString(p_id_json) && strcmp(p_id_json->valuestring, project_id) == 0) {
            cJSON* tasks = cJSON_GetObjectItem(p_item, "tasks");
            cJSON* t_item;
            cJSON_ArrayForEach(t_item, tasks) {
                cJSON* t_id_json = cJSON_GetObjectItem(t_item, "taskID");
                // SỬA LỖI: Kiểm tra NULL trước khi sử dụng
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

__declspec(dllexport) int delete_task_from_project(const char* filepath, const char* project_id, const char* task_id) {
    cJSON* root = read_json_from_file(filepath);
    if (!root) return 0;
    int updated = 0;
    cJSON* p_item;
    cJSON_ArrayForEach(p_item, root) {
        cJSON* p_id_json = cJSON_GetObjectItem(p_item, "projectID");
        // SỬA LỖI: Kiểm tra NULL trước khi sử dụng
        if (p_id_json && cJSON_IsString(p_id_json) && strcmp(p_id_json->valuestring, project_id) == 0) {
            cJSON* tasks = cJSON_GetObjectItem(p_item, "tasks");
            int i = 0;
            cJSON* t_item;
            cJSON_ArrayForEach(t_item, tasks) {
                cJSON* t_id_json = cJSON_GetObjectItem(t_item, "taskID");
                // SỬA LỖI: Kiểm tra NULL trước khi sử dụng
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


__declspec(dllexport) int add_member_to_project(const char* filepath, const char* projectID, const char* memberID) {
    cJSON *root = read_json_from_file(filepath);
    if (!root) return 0;

    int updated = 0;
    cJSON *p_item;
    cJSON_ArrayForEach(p_item, root) {
        cJSON* id_json = cJSON_GetObjectItem(p_item, "projectID");
        // SỬA LỖI: Kiểm tra NULL trước khi sử dụng
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

__declspec(dllexport) int remove_member_from_project(const char* filepath, const char* projectID, const char* memberID) {
    cJSON *root = read_json_from_file(filepath);
    if (!root) return 0;

    int removed = 0;
    cJSON *p_item;
    cJSON_ArrayForEach(p_item, root) {
        cJSON* id_json = cJSON_GetObjectItem(p_item, "projectID");
        // SỬA LỖI: Kiểm tra NULL trước khi sử dụng
        if (id_json && cJSON_IsString(id_json) && strcmp(id_json->valuestring, projectID) == 0) {
            cJSON *members = cJSON_GetObjectItem(p_item, "members");
            if (!cJSON_IsArray(members)) break;

            int member_index = -1;
            int current_index = 0;
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

__declspec(dllexport) int assign_task_to_member(const char* filepath, const char* projectID, const char* taskID, const char* assigneeID) {
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