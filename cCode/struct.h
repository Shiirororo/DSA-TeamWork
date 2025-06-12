#ifndef STRUCT_H
#define STRUCT_H

// Cấu trúc Node chung cho danh sách liên kết đơn
typedef struct Node {
    void* data;
    struct Node* next;
} Node;

// Cấu trúc Node cho danh sách liên kết đôi (có thể dùng trong tương lai)
typedef struct doubleNode {
    void* data;
    struct doubleNode* next;
    struct doubleNode* prev;
} doubleNode;

// Cấu trúc Stack (đã có)
typedef struct Stack {
    Node* top;
} Stack;

// Cấu trúc cho một Task (Công việc)
typedef struct Task {
    char taskID[8];
    char taskName[50];
    char taskDescription[200];
    char assignedTo[8]; // Vẫn giữ là Member ID
    char dueDate[11];
    char status[20];
} Task;

// === THAY ĐỔI BẮT ĐẦU TỪ ĐÂY ===

// [MỚI] Cấu trúc cho một Member (Thành viên)
// Điều này giúp chúng ta lưu trữ thông tin đầy đủ của member trong danh sách liên kết
typedef struct Member {
    char memberID[8];
    char name[50];
    char role[20];
} Member;

// [CẬP NHẬT] Cấu trúc cho một Project (Dự án)
typedef struct Project {
    char projectID[8];
    char projectName[50];
    char projectDescription[200];
    char startDate[11]; // YYYY-MM-DD
    char endDate[11];   // YYYY-MM-DD
    char status[20];
    
    // THAY ĐỔI: Chuyển từ mảng cố định sang danh sách liên kết các thành viên.
    // Mỗi node trong danh sách này sẽ chứa một con trỏ tới một 'struct Member'.
    Node* members; 

    // Giữ nguyên: tasks đã là một danh sách liên kết
    Node* tasks; 
} Project;

// === KẾT THÚC THAY ĐỔI ===

// Cấu trúc cho User (để đăng nhập)
typedef struct User {
    char memberID[8];
    char username[50];
    char password[50];
} User;

typedef struct stack {
    void* data;
    struct stack* next;
} stack;

#endif // STRUCT_H