//******************************************************************************************************//
//File này dùng để xử lý các file định dạng JSON dùng trong dự án, bao gồm các hàm:
//  - load_Project_from_json: Load dữ liệu từ file JSON vào struct Project
//  - load_Member_from_json: Load dữ liệu từ file JSON vào struct Member
//  - save_Project_to_json: Lưu dữ liệu từ struct Project vào file JSON
//  - save_Member_to_json: Lưu dữ liệu từ struct Member vào file JSON
//
//
//******************************************************************************************************//



#include "struct.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <inttypes.h>
#include <ctype.h>
#include "../external/cJSON/cJSON.h"
//******************************************************************************************************//

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif


#define JSON_MEMBER_FILE "../data store/member.json"    
#define JSON_PROJECT_FILE "../data store/project.json"
#define PATH_TO_LASTEST_ID "../data store/lastest_id.txt"
//******************************************************************************************************//
//Xử lí file JSON, load dữ liệu từ file JSON vào struct

// ...existing code...

// Sửa hàm get_next_project_id để nhận tham số đường dẫn file
EXPORT char* get_next_project_id(const char* path) {
    FILE *f = fopen(path, "r+");
    if (f == NULL) {
        perror("Không thể mở file");
        return NULL;
    }

    char buffer[32];
    long line2_pos = 0;
    int line_number = 0;

    while (fgets(buffer, sizeof(buffer), f) != NULL) {
        line_number++;
        if (line_number == 2) {
            line2_pos = ftell(f) - strlen(buffer);
            break;
        }
    }

    if (line_number < 2) {
        fclose(f);
        fprintf(stderr, "File không có đủ 2 dòng\n");
        return NULL;
    }

    size_t pos = strcspn(buffer, "\r\n");
    buffer[pos] = '\0';

    char *original = malloc(strlen(buffer) + 1);
    if (original == NULL) {
        fclose(f);
        fprintf(stderr, "Không đủ bộ nhớ\n");
        return NULL;
    }
    strcpy(original, buffer);

    uint64_t val = strtoull(buffer, NULL, 10);
    val += 1;  // 🔧 Sửa ở đây

    fseek(f, line2_pos, SEEK_SET);
    fprintf(f, "%09" PRIu64 "\n", val);
    fclose(f);

    return original;
}



EXPORT void save_project_to_json(const Project *project) {
    if (project == NULL) return;

    // Tạo JSON object cho project
    cJSON *json = cJSON_CreateObject();
    if (json == NULL) {
        fprintf(stderr, "Lỗi khi tạo JSON object\n");
        return;
    }

    cJSON_AddStringToObject(json, "name", project->name);
    cJSON_AddStringToObject(json, "description", project->description);
    cJSON_AddStringToObject(json, "projectID", project->projectID);
    cJSON_AddStringToObject(json, "ownerID", project->ownerID);
    cJSON_AddStringToObject(json, "startDate", project->startDate);
    cJSON_AddStringToObject(json, "endDate", project->endDate);

    const char *status_str[] = {"Pending", "In Progress", "Completed", "Cancelled"};
    if (project->status >= 0 && project->status <= 3)
        cJSON_AddStringToObject(json, "status", status_str[project->status]);
    else
        cJSON_AddStringToObject(json, "status", "Unknown");

    // Danh sách thành viên
    cJSON *member_array = cJSON_CreateArray();
    for (int i = 0; i < project->currentMember; i++) {
        cJSON *member_obj = cJSON_CreateObject();
        cJSON_AddStringToObject(member_obj, "id", project->memberID[i]);
        cJSON_AddItemToArray(member_array, member_obj);
    }
    cJSON_AddItemToObject(json, "members", member_array);

    // Danh sách task
    cJSON *task_array = cJSON_CreateArray();
    Task *curr = project->tasks;
    int count_task = 0;
    while (curr != NULL) {
        cJSON *task_obj = cJSON_CreateObject();
        cJSON_AddStringToObject(task_obj, "taskID", curr->taskID);
        cJSON_AddStringToObject(task_obj, "projectID", curr->projectID);
        cJSON_AddStringToObject(task_obj, "title", curr->title);
        cJSON_AddStringToObject(task_obj, "description", curr->description);
        cJSON_AddStringToObject(task_obj, "assigneeID", curr->assigneeID);
        cJSON_AddStringToObject(task_obj, "dueDate", curr->dueDate);

        const char *task_status[] = {"Todo", "In Progress", "Done"};
        if (curr->status >= 0 && curr->status <= 2)
            cJSON_AddStringToObject(task_obj, "status", task_status[curr->status]);
        else
            cJSON_AddStringToObject(task_obj, "status", "Unknown");

        cJSON_AddItemToArray(task_array, task_obj);

        curr = curr->next;
        count_task++;
    }
    cJSON_AddItemToObject(json, "tasks", task_array);

    // Chuyển thành chuỗi và ghi ra file
    char *json_str = cJSON_Print(json);
    if (json_str != NULL) {
        FILE *file = fopen(JSON_PROJECT_FILE, "a"); // SỬA DÒNG NÀY
        if (file != NULL) {
            fprintf(file, "%s\n", json_str);
            fclose(file);
        } else {
            fprintf(stderr, "Không thể mở file để ghi\n");
        }
        free(json_str);
    } else {
        fprintf(stderr, "Lỗi khi chuyển JSON thành chuỗi\n");
    }

    // Giải phóng bộ nhớ
    cJSON_Delete(json);
}
// Task make_task (const char *projectID, const char *title, const char *description, const char *assigneeID, const char *dueDate) {
//     Task task;
//     memset(&task, 0, sizeof(Task));  // Đảm bảo struct không chứa dữ liệu rác
//     //Gán trường cơ bản:
//     strncpy(task.title, title, sizeof(task.title) - 1);
//     task.title[sizeof(task.title) - 1] = '\0'; // Đảm bảo kết thúc chuỗi
//     strncpy(task.description, description, sizeof(task.description) - 1);
//     task.description[sizeof(task.description) - 1] = '\0'; // Đảm bảo kết thúc chuỗi
//     task.status = 0; //Auto là Todo
//     strncpy(task.dueDate, dueDate, sizeof(task.dueDate) - 1);
//     task.dueDate[sizeof(task.dueDate) - 1] = '\0';
//     //INSERT ID của thằng đảm nhiệm vòa đây
//     return task;

// }
// Check tất cả các thông tin nhập vào cho 1 dự án

Task make_task(char *taskID, char *projectID, char *title, char *description, char *assigneeID, char *dueDate, int status) {
    Task task;
    memset(&task, 0, sizeof(Task));  // Đảm bảo struct không chứa dữ liệu rác

    // Gán các trường cơ bản
    strncpy(task.taskID, taskID, sizeof(task.taskID) - 1);
    task.taskID[sizeof(task.taskID) - 1] = '\0'; // Đảm bảo kết thúc chuỗi
    strncpy(task.projectID, projectID, sizeof(task.projectID) - 1);
    task.projectID[sizeof(task.projectID) - 1] = '\0';
    strncpy(task.title, title, sizeof(task.title) - 1);
    task.title[sizeof(task.title) - 1] = '\0';
    strncpy(task.description, description, sizeof(task.description) - 1);
    task.description[sizeof(task.description) - 1] = '\0';
    strncpy (task.assigneeID, assigneeID, sizeof(task.assigneeID) - 1);
    task.assigneeID[sizeof(task.assigneeID) - 1] = '\0';
    strncpy(task.dueDate, dueDate, sizeof(task.dueDate) - 1);   
    task.dueDate[sizeof(task.dueDate) - 1] = '\0';
    task.status = status; // 0: Todo, 1: In Progress, 2: Done
    task.next = NULL; // Khởi tạo con trỏ next là NULL
    return task;
}

//Thay hàm này thành hàm chuẩn hóa
// EXPORT int check_valid_name (const char *name) {
//     if (name == NULL || *name == '\0') return 0;
//     size_t len = strlen(name);
//     if (len < 3 || len > 20) return 0;
//     int space_count = 0;
//     int current_consecutive_letters = 0;
//     for (size_t i = 0; i < len; i++) {
//         if (name[i] == ' ') {
//             space_count++;
//             current_consecutive_letters = 0;
//             if (space_count > 3) return 0;
//             continue;
//         }
//         if (current_consecutive_letters == 0) {
//             if (name[i] < 'A' || name[i] > 'Z') return 0; //First letter must be uppercase
//         }
//         else {
//             if (name[i] < 'a' || name[i] > 'z') return 0; //Must be letter if not first
//         }
//         current_consecutive_letters++;
//     }
//     return 1;
// }





// ...existing code...












// Project create_project(const char* creator, const char *name, const char *desc) {
//     Project project;
//     memset(&project, 0, sizeof(Project));  // Đảm bảo struct không chứa dữ liệu rác

//     // Gán các trường cơ bản
//     strncpy(project.name, name, sizeof(project.name) - 1);
//     strncpy(project.description, desc, sizeof(project.description) - 1);
//     project.description[sizeof(project.description) - 1] = '\0'; // Đảm bảo kết thúc chuỗi
//     strncpy(project.ownerID, creator, sizeof(project.ownerID) - 1);
//     project.ownerID[sizeof(project.ownerID) - 1] = '\0';
//     project.status = 0;

//     // Lấy project ID
//     char *id = get_next_project_id(PATH_TO_LASTEST_ID);
//     if (id == NULL) {
//         fprintf(stderr, "Lỗi: Không thể tạo project ID.\n");
//         exit(EXIT_FAILURE);  // Hoặc có thể trả về project trống tuỳ cách bạn muốn xử lý
//     }

//     // Gán ID một cách an toàn
//     snprintf(project.projectID, sizeof(project.projectID), "%s", id);
//     free(id);

//     // TODO: save_Project_to_json(project);

//     return project;
// }


EXPORT Project create_project(char *name, char *ownerID, char memberID[MAX_MEMBER][8], int currentMember, char *description, char *startDate, char *endDate, int status, Task *tasks) {
    Project project;
    memset(&project, 0, sizeof(Project));

    strncpy(project.name, name, sizeof(project.name) - 1);
    project.name[sizeof(project.name) - 1] = '\0';

    // Lấy projectID tự động
    char *id = get_next_project_id(PATH_TO_LASTEST_ID);
    if (id == NULL) {
        fprintf(stderr, "Không thể lấy project ID\n");
        exit(EXIT_FAILURE);
    }
    strncpy(project.projectID, id, sizeof(project.projectID) - 1);
    project.projectID[sizeof(project.projectID) - 1] = '\0';
    free(id);

    strncpy(project.ownerID, ownerID, sizeof(project.ownerID) - 1);
    project.ownerID[sizeof(project.ownerID) - 1] = '\0';

    for (int i = 0; i < currentMember; i++) {
        strncpy(project.memberID[i], memberID[i], sizeof(project.memberID[i]) - 1);
        project.memberID[i][sizeof(project.memberID[i]) - 1] = '\0';
    }
    project.currentMember = currentMember;

    strncpy(project.description, description, sizeof(project.description) - 1);
    project.description[sizeof(project.description) - 1] = '\0';

    strncpy(project.startDate, startDate, sizeof(project.startDate) - 1);
    project.startDate[sizeof(project.startDate) - 1] = '\0';

    strncpy(project.endDate, endDate, sizeof(project.endDate) - 1);
    project.endDate[sizeof(project.endDate) - 1] = '\0';

    project.status = status;
    project.tasks = tasks;

    return project;
}



//ham make_task co van de
//duong dan den file json khong dung 146
//ham get_next_project_id co van de


//in id duoi dang string tat ca vao 1