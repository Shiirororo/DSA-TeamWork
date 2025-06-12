#ifndef VALIDATION_H
#define VALIDATION_H

#include <stdio.h>
#include <string.h>
#include <ctype.h> // Để dùng isdigit, isspace

// Trả về 1 nếu hợp lệ, 0 nếu không hợp lệ

// Kiểm tra xem một chuỗi có rỗng hoặc chỉ chứa khoảng trắng không
int is_string_empty(const char* str);

// Kiểm tra ID có đúng định dạng (Prefix + Số) không
int is_valid_id_format(const char* id, const char prefix, int num_digits);

// [MỚI] Kiểm tra xem trạng thái có hợp lệ không (ví dụ: "Todo", "In Progress", "Done")
int is_valid_status(const char* status);

#endif // VALIDATION_H