#ifndef IMPLEMENT_H
#define IMPLEMENT_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cJSON.h"
#include "struct.h"

// =================================================================
// I. CÁC HÀM CƠ BẢN VỀ CẤU TRÚC DỮ LIỆU (DSLK, STACK)
// =================================================================

// --- Danh sách liên kết ---
Node* createNode(void* data);
Node* appendNode(Node* head, Node* newNode);
Node* prependNode(Node* head, Node* newNode);
Node* deleteNode(Node* head, void* data_to_delete, int (*compare_func)(const void*, const void*));
int countNodes(Node* head);
void printList(Node* head, void (*print_func)(void*));

// --- Stack ---
Stack* createStack();
void push(Stack* stack, void* data);
void* pop(Stack* stack);
int isStackEmpty(Stack* stack);

// =================================================================
// II. CÁC HÀM TIỆN ÍCH (FILE I/O)
// =================================================================
cJSON* read_json_from_file(const char* filepath);
int write_json_to_file(const char* filepath, cJSON* json);


// =================================================================
// III. CÁC HÀM CHUYỂN ĐỔI (JSON <-> DANH SÁCH LIÊN KẾT)
// =================================================================

// --- Chuyển đổi TỪ JSON sang Danh sách liên kết ---
Node* cjsonToTaskList(cJSON* tasks_json_array);
Node* cjsonToMemberList(cJSON* member_ids_json_array, cJSON* all_members_json_array);
Node* cjsonToProjectList(cJSON* projects_json_array, const char* member_filepath);

// --- Chuyển đổi TỪ Danh sách liên kết sang JSON ---
cJSON* taskListToCjson(Node* head);
cJSON* memberListToCjson(Node* head);
cJSON* projectListToCjson(Node* head);


// =================================================================
// IV. CÁC HÀM QUẢN LÝ BỘ NHỚ
// =================================================================
void freeTaskList(Node* head);
void freeMemberList(Node* head);
void freeProjectList(Node* head);


#endif // IMPLEMENT_H