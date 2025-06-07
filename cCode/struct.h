//******************************************************************************************************//
// Các struct dữ liệu dùng trong Project
//  - Member: Chứa thông tin của một thành viên trong dự án
//
//  - Project: Chứa thông tin của một dự án
//
//
//
//******************************************************************************************************//




#ifndef STRUCT_H
#define STRUCT_H
#include <stdio.h>
#include <string.h>

#define MIN_MEMBER 3
#define MAX_MEMBER 10
#define Member_Array_size 100


typedef struct Member {
    char id[8];
    long phoneNumber;
    char name[50];
    char role[20];
    int age;
    char address[200];
    char email[100];
} Member;


//Sử dụng danh sách liên kết để kiểm soát tiến độ công việc
typedef struct Task {
    char taskID[11];
    char projectID[10];
    char title[100];
    char description[200];
    char assigneeID[8];
    char dueDate[20];
    int status;  // 0: Todo, 1: In Progress, 2: Done
    struct Task* next;
} Task;


typedef struct Project {
    char name[50];
    char projectID[11];
    char ownerID[8];
    char memberID[MAX_MEMBER][8];
    int currentMember;
    char description[200];
    char startDate[20];
    char endDate[20];
    int status; //0: Pending, 1: Inprogress, 2: Completed, 3: Cancelled
    //Member members[10];
    Task* tasks;
} Project;



//Cấu trúc dữ liệu dùng trong Project
typedef struct Node {
    void* data;
    struct Node* next;
} Node;
typedef struct doubleNode {
    void* data;
    struct doubleNode* next;
    struct doubleNode* prev;
} doubleNode;

typedef struct stack {
    void* data;
    struct stack* next;
} stack;

typedef struct memberList {
    Member* data;
    int size;
    int cap;
} memberList;






#endif // STRUCT_H