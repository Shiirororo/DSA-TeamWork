#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cJSON.h"
#include "struct.h"

// --- HÀM NỘI BỘ ---
cJSON* read_json_from_file(const char* filepath) {
    FILE *file = fopen(filepath, "r");
    if (!file) return NULL;
    fseek(file, 0, SEEK_END);
    long length = ftell(file);
    fseek(file, 0, SEEK_SET);
    char *data = (char *)malloc(length + 1);
    if (!data) { fclose(file); return NULL; }
    fread(data, 1, length, file);
    data[length] = '\0';
    fclose(file);
    cJSON *json = cJSON_Parse(data);
    free(data);
    return json;
}

void write_json_to_file(const char* filepath, cJSON* json) {
    FILE *file = fopen(filepath, "w");
    if (file) {
        char *out = cJSON_Print(json);
        if (out) {
            fprintf(file, "%s", out);
            free(out);
        }
        fclose(file);
    }
}

// --- CÁC HÀM EXPORT ---
__declspec(dllexport) void free_c_string(void* ptr) {
    if(ptr) free(ptr);
}

__declspec(dllexport) int create_project(const char* projects_filepath, const char* projectID, const char* name, const char* description, const char* ownerID) {
    if (!projectID) return 0;
    cJSON *root = read_json_from_file(projects_filepath);
    if (!cJSON_IsArray(root)) { cJSON_Delete(root); root = cJSON_CreateArray(); }

    cJSON *project = cJSON_CreateObject();
    cJSON_AddStringToObject(project, "projectID", projectID);
    cJSON_AddStringToObject(project, "name", name);
    cJSON_AddStringToObject(project, "description", description);
    cJSON_AddStringToObject(project, "ownerID", ownerID);
    cJSON_AddStringToObject(project, "status", "Pending");

    cJSON *members = cJSON_CreateArray();
    cJSON *owner_member = cJSON_CreateObject();
    cJSON_AddStringToObject(owner_member, "id", ownerID);
    cJSON_AddItemToArray(members, owner_member);
    
    cJSON_AddItemToObject(project, "members", members);
    cJSON_AddItemToObject(project, "tasks", cJSON_CreateArray());
    cJSON_AddItemToArray(root, project);

    write_json_to_file(projects_filepath, root);
    cJSON_Delete(root);
    return 1;
}

__declspec(dllexport) int add_task_to_project(const char* projects_filepath, const char* projectID, const char* taskID, const char* title, const char* description) {
    if (!taskID) return 0;
    cJSON *root = read_json_from_file(projects_filepath);
    if (!cJSON_IsArray(root)) { cJSON_Delete(root); return 0; }

    int found = 0;
    cJSON *p_item;
    cJSON_ArrayForEach(p_item, root) {
        cJSON *p_id_json = cJSON_GetObjectItem(p_item, "projectID");
        if (p_id_json && cJSON_IsString(p_id_json) && strcmp(p_id_json->valuestring, projectID) == 0) {
            found = 1;
            cJSON *tasks = cJSON_GetObjectItem(p_item, "tasks");
            if (!cJSON_IsArray(tasks)) { tasks = cJSON_CreateArray(); cJSON_ReplaceItemInObject(p_item, "tasks", tasks); }
            cJSON *new_task = cJSON_CreateObject();
            cJSON_AddStringToObject(new_task, "taskID", taskID);
            cJSON_AddStringToObject(new_task, "title", title);
            cJSON_AddStringToObject(new_task, "description", description);
            cJSON_AddStringToObject(new_task, "assigneeID", "");
            cJSON_AddStringToObject(new_task, "status", "Todo");
            cJSON_AddItemToArray(tasks, new_task);
            break;
        }
    }

    if(found) write_json_to_file(projects_filepath, root);
    cJSON_Delete(root);
    return found;
}

// =============================================================
// ==================== HÀM MỚI ĐƯỢC THÊM ======================
// =============================================================
__declspec(dllexport) int delete_task_from_project(const char* filepath, const char* projectID, const char* taskID) {
    cJSON *root = read_json_from_file(filepath);
    if (!root) return 0;

    int deleted = 0;
    cJSON *p_item;
    cJSON_ArrayForEach(p_item, root) {
        cJSON *p_id_json = cJSON_GetObjectItem(p_item, "projectID");
        if (p_id_json && cJSON_IsString(p_id_json) && strcmp(p_id_json->valuestring, projectID) == 0) {
            cJSON *tasks = cJSON_GetObjectItem(p_item, "tasks");
            if (!cJSON_IsArray(tasks)) break;

            int task_index = -1;
            int current_index = 0;
            cJSON *t_item;
            cJSON_ArrayForEach(t_item, tasks) {
                cJSON *t_id_json = cJSON_GetObjectItem(t_item, "taskID");
                if (t_id_json && cJSON_IsString(t_id_json) && strcmp(t_id_json->valuestring, taskID) == 0) {
                    task_index = current_index;
                    break;
                }
                current_index++;
            }
            if (task_index != -1) {
                cJSON_DeleteItemFromArray(tasks, task_index);
                deleted = 1;
            }
            break;
        }
    }
    
    if (deleted) write_json_to_file(filepath, root);
    cJSON_Delete(root);
    return deleted;
}
// =============================================================

__declspec(dllexport) int delete_project_by_id(const char* filepath, const char* projectID) {
    cJSON *root = read_json_from_file(filepath);
    if (!root) return 0;
    cJSON *new_root = cJSON_CreateArray();
    int deleted = 0;
    cJSON *item;
    cJSON_ArrayForEach(item, root) {
        cJSON *id_json = cJSON_GetObjectItem(item, "projectID");
        if (cJSON_IsString(id_json) && (strcmp(id_json->valuestring, projectID) == 0)) { deleted = 1; } 
        else { cJSON_AddItemToArray(new_root, cJSON_Duplicate(item, 1)); }
    }
    if (deleted) write_json_to_file(filepath, new_root);
    cJSON_Delete(root); cJSON_Delete(new_root);
    return deleted;
}

__declspec(dllexport) int update_project_by_id(const char* filepath, const char* projectID, const char* newName, const char* newDescription) {
    cJSON *root = read_json_from_file(filepath);
    if (!root) return 0;
    int updated = 0;
    cJSON *item;
    cJSON_ArrayForEach(item, root) {
        cJSON *id_json = cJSON_GetObjectItem(item, "projectID");
        if (cJSON_IsString(id_json) && strcmp(id_json->valuestring, projectID) == 0) {
            cJSON_ReplaceItemInObject(item, "name", cJSON_CreateString(newName));
            cJSON_ReplaceItemInObject(item, "description", cJSON_CreateString(newDescription));
            updated = 1; break;
        }
    }
    if (updated) write_json_to_file(filepath, root);
    cJSON_Delete(root);
    return updated;
}

__declspec(dllexport) int update_task_status(const char* filepath, const char* projectID, const char* taskID, const char* newStatus) {
    cJSON *root = read_json_from_file(filepath);
    if (!root) return 0;
    int updated = 0;
    cJSON *p_item;
    cJSON_ArrayForEach(p_item, root) {
        cJSON *p_id_json = cJSON_GetObjectItem(p_item, "projectID");
        if (p_id_json && cJSON_IsString(p_id_json) && strcmp(p_id_json->valuestring, projectID) == 0) {
            cJSON *tasks = cJSON_GetObjectItem(p_item, "tasks");
            cJSON *t_item;
            cJSON_ArrayForEach(t_item, tasks) {
                cJSON *t_id_json = cJSON_GetObjectItem(t_item, "taskID");
                if (t_id_json && cJSON_IsString(t_id_json) && strcmp(t_id_json->valuestring, taskID) == 0) {
                    cJSON_ReplaceItemInObject(t_item, "status", cJSON_CreateString(newStatus));
                    updated = 1; break;
                }
            }
            if(updated) break;
        }
    }
    if (updated) write_json_to_file(filepath, root);
    cJSON_Delete(root);
    return updated;
}