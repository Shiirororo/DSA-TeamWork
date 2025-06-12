#include "implement.h"

// =================================================================
// I. CÁC HÀM CƠ BẢN VỀ CẤU TRÚC DỮ LIỆU (DSLK, STACK)
// =================================================================

// --- Danh sách liên kết ---

Node* createNode(void* data) {
    Node* newNode = (Node*)malloc(sizeof(Node));
    if (newNode == NULL) {
        perror("Failed to allocate memory for new node");
        exit(EXIT_FAILURE);
    }
    newNode->data = data;
    newNode->next = NULL;
    return newNode;
}

Node* appendNode(Node* head, Node* newNode) {
    if (head == NULL) {
        return newNode;
    }
    Node* current = head;
    while (current->next != NULL) {
        current = current->next;
    }
    current->next = newNode;
    return head;
}

Node* prependNode(Node* head, Node* newNode) {
    newNode->next = head;
    return newNode;
}

// Lưu ý: Các hàm deleteNode, countNodes, printList cần bạn tự triển khai logic
// so sánh và in ấn tùy theo kiểu dữ liệu của `void* data`.
// Dưới đây là các hàm mẫu, bạn có thể cần chỉnh sửa.

int countNodes(Node* head) {
    int count = 0;
    Node* current = head;
    while (current != NULL) {
        count++;
        current = current->next;
    }
    return count;
}


// --- Stack ---

Stack* createStack() {
    Stack* stack = (Stack*)malloc(sizeof(Stack));
    if (stack == NULL) {
        perror("Failed to allocate memory for stack");
        exit(EXIT_FAILURE);
    }
    stack->top = NULL;
    return stack;
}

void push(Stack* stack, void* data) {
    Node* newNode = createNode(data);
    newNode->next = stack->top;
    stack->top = newNode;
}

void* pop(Stack* stack) {
    if (isStackEmpty(stack)) {
        return NULL;
    }
    Node* temp = stack->top;
    void* data = temp->data;
    stack->top = stack->top->next;
    free(temp);
    return data;
}

int isStackEmpty(Stack* stack) {
    return stack->top == NULL;
}


// =================================================================
// II. CÁC HÀM TIỆN ÍCH (FILE I/O)
// (Đã di chuyển từ createProject.c để quản lý tập trung)
// =================================================================

cJSON* read_json_from_file(const char* filepath) {
    FILE* file = fopen(filepath, "rb");
    if (file == NULL) {
        perror("Error opening file");
        return NULL;
    }

    fseek(file, 0, SEEK_END);
    long length = ftell(file);
    fseek(file, 0, SEEK_SET);

    char* buffer = (char*)malloc(length + 1);
    if (buffer == NULL) {
        fclose(file);
        perror("Error allocating memory for file buffer");
        return NULL;
    }

    fread(buffer, 1, length, file);
    fclose(file);
    buffer[length] = '\0';

    cJSON* json = cJSON_Parse(buffer);
    free(buffer);
    return json;
}

int write_json_to_file(const char* filepath, cJSON* json) {
    char* json_string = cJSON_Print(json);
    if (json_string == NULL) {
        fprintf(stderr, "Failed to print cJSON object.\n");
        return 0; // Thất bại
    }

    FILE* file = fopen(filepath, "w");
    if (file == NULL) {
        perror("Error opening file for writing");
        free(json_string);
        return 0; // Thất bại
    }

    fprintf(file, "%s", json_string);
    fclose(file);
    free(json_string);
    return 1; // Thành công
}

// =================================================================
// III. CÁC HÀM CHUYỂN ĐỔI (JSON <-> DANH SÁCH LIÊN KẾT)
// =================================================================

// --- Chuyển đổi TỪ JSON sang Danh sách liên kết ---

Node* cjsonToTaskList(cJSON* tasks_json_array) {
    if (!cJSON_IsArray(tasks_json_array)) return NULL;

    Node* head = NULL;
    cJSON* task_json;
    cJSON_ArrayForEach(task_json, tasks_json_array) {
        Task* new_task = (Task*)malloc(sizeof(Task));
        if (!new_task) continue;

        strcpy(new_task->taskID, cJSON_GetObjectItem(task_json, "id")->valuestring);
        strcpy(new_task->taskName, cJSON_GetObjectItem(task_json, "name")->valuestring);
        strcpy(new_task->taskDescription, cJSON_GetObjectItem(task_json, "description")->valuestring);
        strcpy(new_task->assignedTo, cJSON_GetObjectItem(task_json, "assignedTo")->valuestring);
        strcpy(new_task->dueDate, cJSON_GetObjectItem(task_json, "dueDate")->valuestring);
        strcpy(new_task->status, cJSON_GetObjectItem(task_json, "status")->valuestring);

        head = appendNode(head, createNode(new_task));
    }
    return head;
}

Node* cjsonToMemberList(cJSON* member_ids_json_array, cJSON* all_members_json_array) {
    if (!cJSON_IsArray(member_ids_json_array) || !cJSON_IsArray(all_members_json_array)) return NULL;

    Node* head = NULL;
    cJSON* member_id_json;
    cJSON_ArrayForEach(member_id_json, member_ids_json_array) {
        const char* current_member_id = member_id_json->valuestring;
        cJSON* member_detail_json;
        cJSON_ArrayForEach(member_detail_json, all_members_json_array) {
            if (strcmp(current_member_id, cJSON_GetObjectItem(member_detail_json, "id")->valuestring) == 0) {
                Member* new_member = (Member*)malloc(sizeof(Member));
                if (!new_member) break;

                strcpy(new_member->memberID, current_member_id);
                strcpy(new_member->name, cJSON_GetObjectItem(member_detail_json, "name")->valuestring);
                strcpy(new_member->role, cJSON_GetObjectItem(member_detail_json, "role")->valuestring);

                head = appendNode(head, createNode(new_member));
                break;
            }
        }
    }
    return head;
}

Node* cjsonToProjectList(cJSON* projects_json_array, const char* member_filepath) {
    if (!cJSON_IsArray(projects_json_array)) return NULL;

    cJSON* all_members_json = read_json_from_file(member_filepath);
    if (all_members_json == NULL) return NULL;

    Node* head = NULL;
    cJSON* project_json;
    cJSON_ArrayForEach(project_json, projects_json_array) {
        Project* new_project = (Project*)malloc(sizeof(Project));
        if (!new_project) continue;

        strcpy(new_project->projectID, cJSON_GetObjectItem(project_json, "projectID")->valuestring);
        strcpy(new_project->projectName, cJSON_GetObjectItem(project_json, "projectName")->valuestring);
        strcpy(new_project->projectDescription, cJSON_GetObjectItem(project_json, "projectDescription")->valuestring);
        strcpy(new_project->startDate, cJSON_GetObjectItem(project_json, "startDate")->valuestring);
        strcpy(new_project->endDate, cJSON_GetObjectItem(project_json, "endDate")->valuestring);
        strcpy(new_project->status, cJSON_GetObjectItem(project_json, "status")->valuestring);

        new_project->tasks = cjsonToTaskList(cJSON_GetObjectItem(project_json, "tasks"));
        new_project->members = cjsonToMemberList(cJSON_GetObjectItem(project_json, "members"), all_members_json);

        head = appendNode(head, createNode(new_project));
    }
    
    cJSON_Delete(all_members_json);
    return head;
}

// --- Chuyển đổi TỪ Danh sách liên kết sang JSON ---
// [MỚI] Các hàm này rất quan trọng để ghi dữ liệu trở lại file

cJSON* taskListToCjson(Node* head) {
    cJSON* tasks_json_array = cJSON_CreateArray();
    Node* current = head;
    while (current != NULL) {
        Task* task_data = (Task*)current->data;
        cJSON* task_json = cJSON_CreateObject();
        cJSON_AddStringToObject(task_json, "id", task_data->taskID);
        cJSON_AddStringToObject(task_json, "name", task_data->taskName);
        cJSON_AddStringToObject(task_json, "description", task_data->taskDescription);
        cJSON_AddStringToObject(task_json, "assignedTo", task_data->assignedTo);
        cJSON_AddStringToObject(task_json, "dueDate", task_data->dueDate);
        cJSON_AddStringToObject(task_json, "status", task_data->status);
        cJSON_AddItemToArray(tasks_json_array, task_json);
        current = current->next;
    }
    return tasks_json_array;
}

cJSON* memberListToCjson(Node* head) {
    cJSON* member_ids_json_array = cJSON_CreateArray();
    Node* current = head;
    while (current != NULL) {
        Member* member_data = (Member*)current->data;
        cJSON_AddItemToArray(member_ids_json_array, cJSON_CreateString(member_data->memberID));
        current = current->next;
    }
    return member_ids_json_array;
}

cJSON* projectListToCjson(Node* head) {
    cJSON* projects_json_array = cJSON_CreateArray();
    Node* current = head;
    while (current != NULL) {
        Project* project_data = (Project*)current->data;
        cJSON* project_json = cJSON_CreateObject();

        cJSON_AddStringToObject(project_json, "projectID", project_data->projectID);
        cJSON_AddStringToObject(project_json, "projectName", project_data->projectName);
        cJSON_AddStringToObject(project_json, "projectDescription", project_data->projectDescription);
        cJSON_AddStringToObject(project_json, "startDate", project_data->startDate);
        cJSON_AddStringToObject(project_json, "endDate", project_data->endDate);
        cJSON_AddStringToObject(project_json, "status", project_data->status);
        
        cJSON_AddItemToObject(project_json, "members", memberListToCjson(project_data->members));
        cJSON_AddItemToObject(project_json, "tasks", taskListToCjson(project_data->tasks));

        cJSON_AddItemToArray(projects_json_array, project_json);
        current = current->next;
    }
    return projects_json_array;
}


// =================================================================
// IV. CÁC HÀM QUẢN LÝ BỘ NHỚ
// =================================================================

void freeTaskList(Node* head) {
    Node* current = head;
    while (current != NULL) {
        Node* temp = current;
        current = current->next;
        free(temp->data);
        free(temp);
    }
}

void freeMemberList(Node* head) {
    Node* current = head;
    while (current != NULL) {
        Node* temp = current;
        current = current->next;
        free(temp->data);
        free(temp);
    }
}

void freeProjectList(Node* head) {
    Node* current = head;
    while (current != NULL) {
        Project* project_data = (Project*)current->data;
        
        freeTaskList(project_data->tasks);
        freeMemberList(project_data->members);

        Node* temp = current;
        current = current->next;
        free(temp->data);
        free(temp);
    }
}