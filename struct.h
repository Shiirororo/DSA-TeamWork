#ifndef STRUCT_H
#define STRUCT_H

#define MAX_STR_LEN 100

typedef struct {
    char id[9];             // 8 số + '\0'
    char role[20];          // Chuỗi vai trò như "admin", "user"
    char name[MAX_STR_LEN];
    char email[MAX_STR_LEN];
    char phoneNumber[11];   // 10 số + '\0'
    char address[MAX_STR_LEN];
} Member;

#endif
