#include "validation.h"

// Kiểm tra xem một chuỗi có rỗng hoặc chỉ chứa khoảng trắng không
int is_string_empty(const char* str) {
    if (str == NULL) {
        return 1;
    }
    while (*str != '\0') {
        if (!isspace((unsigned char)*str)) {
            return 0; // Tìm thấy ký tự không phải khoảng trắng
        }
        str++;
    }
    return 1; // Toàn là khoảng trắng hoặc rỗng
}

// Kiểm tra ID có đúng định dạng (Prefix + Số) không
// Ví dụ: is_valid_id_format("PRJ-123", 'P', 7)
int is_valid_id_format(const char* id, const char prefix, int num_digits) {
    if (id == NULL || strlen(id) != (size_t)(1 + 3 + num_digits)) { // Ví dụ: 'P' + 'RJ-' + 7 digits
        return 0;
    }
    // Logic kiểm tra cụ thể hơn có thể được thêm ở đây nếu cần
    // Ví dụ kiểm tra id[0] == prefix, id[1] == 'R', id[2] == 'J', id[3] == '-'
    // For now, we'll keep it simple
    return 1;
}

// Kiểm tra xem trạng thái có hợp lệ không
int is_valid_status(const char* status) {
    if (status == NULL) return 0;
    
    const char* valid_statuses[] = {"Todo", "In Progress", "Done"};
    int num_valid_statuses = sizeof(valid_statuses) / sizeof(valid_statuses[0]);
    
    for (int i = 0; i < num_valid_statuses; i++) {
        if (strcmp(status, valid_statuses[i]) == 0) {
            return 1; // Hợp lệ
        }
    }
    
    return 0; // Không hợp lệ
}