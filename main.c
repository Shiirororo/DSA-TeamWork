#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "struct.h"
#include "validation.h"
#include "cJSON.h"

#define JSON_FILE "members.json"

// Hàm đọc toàn bộ file thành chuỗi
char* readFile(const char* filename) {
    FILE* f = fopen(filename, "rb");
    if (!f) {
        perror("Failed to open file");
        return NULL;
    }

    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    fseek(f, 0, SEEK_SET);

    char* buffer = (char*)malloc(size + 1);
    if (!buffer) {
        fclose(f);
        perror("Malloc failed");
        return NULL;
    }

    size_t readBytes = fread(buffer, 1, size, f);
    if (readBytes != size) {
        perror("Failed to read file fully");
        free(buffer);
        fclose(f);
        return NULL;
    }

    buffer[size] = '\0';
    fclose(f);
    return buffer;
}

int main() {
    char* jsonString = readFile(JSON_FILE);
    if (!jsonString) return 1;

    cJSON* json = cJSON_Parse(jsonString);
    free(jsonString);

    if (!json) {
        printf("JSON parse error\n");
        return 1;
    }

    if (!cJSON_IsArray(json)) {
        printf("JSON root is not an array\n");
        cJSON_Delete(json);
        return 1;
    }

    int size = cJSON_GetArraySize(json);
    Member* members = (Member*)malloc(sizeof(Member) * size);
    if (!members) {
        printf("Malloc failed\n");
        cJSON_Delete(json);
        return 1;
    }

    for (int i = 0; i < size; i++) {
        cJSON* item = cJSON_GetArrayItem(json, i);
        if (!cJSON_IsObject(item)) {
            printf("Item %d is not an object\n", i);
            continue;
        }

        cJSON* id = cJSON_GetObjectItem(item, "id");
        cJSON* role = cJSON_GetObjectItem(item, "role");
        cJSON* name = cJSON_GetObjectItem(item, "name");
        cJSON* email = cJSON_GetObjectItem(item, "email");
        cJSON* phoneNumber = cJSON_GetObjectItem(item, "phoneNumber");
        cJSON* address = cJSON_GetObjectItem(item, "address");

        if (!cJSON_IsString(id) || !cJSON_IsNumber(role) ||
            !cJSON_IsString(name) || !cJSON_IsString(email) ||
            !cJSON_IsString(phoneNumber) || !cJSON_IsString(address)) {
            printf("Missing or invalid fields in member %d\n", i);
            continue;
        }

        // Copy dữ liệu an toàn
        strncpy(members[i].id, id->valuestring, 8);
        members[i].id[8] = '\0';

        if (role->valueint == 1)
            strcpy(members[i].role, "admin");
        else if (role->valueint == 0)
            strcpy(members[i].role, "user");
        else
            strcpy(members[i].role, "unknown");

        strncpy(members[i].name, name->valuestring, MAX_STR_LEN - 1);
        members[i].name[MAX_STR_LEN - 1] = '\0';

        strncpy(members[i].email, email->valuestring, MAX_STR_LEN - 1);
        members[i].email[MAX_STR_LEN - 1] = '\0';

        strncpy(members[i].phoneNumber, phoneNumber->valuestring, sizeof(members[i].phoneNumber) - 1);
        members[i].phoneNumber[sizeof(members[i].phoneNumber) - 1] = '\0';

        strncpy(members[i].address, address->valuestring, MAX_STR_LEN - 1);
        members[i].address[MAX_STR_LEN - 1] = '\0';

        // Gọi hàm kiểm tra
        if (checkMember(&members[i])) {
            printf("✅ Member %d is valid: %s (%s)\n", i + 1, members[i].name, members[i].role);
        } else {
            printf("❌ Member %d is invalid\n", i + 1);
        }
    }

    free(members);
    cJSON_Delete(json);
    return 0;
}
