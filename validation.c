#include "validation.h"
#include <ctype.h>
#include <string.h>
#include <stdio.h>

// ID phải gồm đúng 8 ký tự số ('0' - '9')
bool isValidMemberID(const char* id) {
    if (id == NULL) return false;
    if (strlen(id) != 8) return false;
    for (int i = 0; i < 8; i++) {
        if (!isdigit((unsigned char)id[i])) return false;
    }
    return true;
}

// Tên chỉ chứa chữ cái (a-z, A-Z) và dấu cách, không rỗng
bool isValidName(const char* name) {
    if (name == NULL) return false;
    int len = strlen(name);
    if (len == 0) return false;
    for (int i = 0; i < len; i++) {
        if (!isalpha((unsigned char)name[i]) && name[i] != ' ')
            return false;
    }
    return true;
}

// Email đơn giản: phải có '@' và '.' sau '@'
bool isValidEmailFormat(const char* email) {
    if (email == NULL) return false;
    const char* at = strchr(email, '@');
    if (at == NULL || at == email) return false;  // phải có '@' và không ở đầu
    const char* dot = strchr(at, '.');
    if (dot == NULL || dot == at + 1) return false;  // '.' phải nằm sau '@' và không ngay sau '@'
    if (*(dot + 1) == '\0') return false;  // '.' không được ở cuối
    return true;
}

// Số điện thoại gồm đúng 10 chữ số (chuỗi ký tự)
bool isValidPhoneNumber(const char* phoneNumber) {
    if (phoneNumber == NULL) return false;
    if (strlen(phoneNumber) != 10) return false;
    for (int i = 0; i < 10; i++) {
        if (!isdigit((unsigned char)phoneNumber[i])) return false;
    }
    return true;
}

// Hàm kiểm tra tổng thể 1 member (giả sử member là struct chứa id, name, email, phoneNumber)
#include "struct.h"
bool checkMember(const Member* member) {
    if (!isValidMemberID(member->id)) {
        printf("Invalid ID: %s\n", member->id);
        return false;
    }
    if (!isValidName(member->name)) {
        printf("Invalid Name: %s\n", member->name);
        return false;
    }
    if (!isValidEmailFormat(member->email)) {
        printf("Invalid Email: %s\n", member->email);
        return false;
    }
    // member->phoneNumber đang là char[11], kiểm tra chuỗi số 10 ký tự + '\0'
    if (!isValidPhoneNumber(member->phoneNumber)) {
        printf("Invalid Phone Number: %s\n", member->phoneNumber);
        return false;
    }
    return true;
}
