#ifndef VALIDATION_H
#define VALIDATION_H

#include <stdbool.h>

// Kiểm tra ID hợp lệ: đúng 8 ký tự số
bool isValidMemberID(const char* id);

// Kiểm tra tên hợp lệ: chỉ gồm chữ cái và khoảng trắng, không rỗng
bool isValidName(const char* name);

// Kiểm tra email hợp lệ: có dạng abc@xyz.domain 
bool isValidEmailFormat(const char* email);

// Kiểm tra số điện thoại hợp lệ: đúng 10 chữ số, không chứa ký tự khác
bool isValidPhoneNumber(const char* phoneNumber);

// Hàm kiểm tra tổng thể Member 
bool checkMember(const void* member);

#endif // VALIDATION_H
