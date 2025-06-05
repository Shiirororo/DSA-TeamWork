#include <iostream>

using namespace std;

//1. khai bao cau truc dslk don so nguyen
//khai bao 1 cai node
struct Node{
int data;
struct Node* pNext;
};

typedef struct Node NODE;

struct list{
Node* pHead;
Node* pTail;
};
typedef struct list LIST;

//2. khoi tao cau truc dslk don so nguyen
//khoi tao list
void KhoiTao(LIST& l){
l.pHead=NULL;
l.pTail=NULL;
}
//khoi tao 1 cai node
NODE* KhoiTaoNode(int x){
NODE* p= new NODE;
if(p==NULL){
    cout<<"\n khong du bo nho de cap phat";
    return NULL;
}
p->data=x;
p->pNext=NULL;
return p;
}

//3.ham them vao dau dslk
void themvaodau(LIST& l, NODE* p){
if(l.pHead==NULL){
    l.pHead=l.pTail=p;//dau cuoi deu la p
}
else{
    p->pNext=l.pHead;
    l.pHead=p;//cap nhap lai p
}
}

//4.ham them vao cuoi dslk
void themvaocuoi(LIST&l, NODE* p){
if(l.pHead==NULL){
    l.pHead=l.pTail=p;
}
else{
    l.pTail->pNext=p;
    l.pTail=p;
}
}

//5.ham xuat dslk
void Xuatdanhsach(LIST l){
for(NODE* k=l.pHead; k!=NULL; k=k->pNext){
    cout<<k->data<<" ";
}
}

//bai 4. them node vao vi tri bat ky
void ThemVaoBatKy(LIST& l, NODE*p, int vt){
//ham them vao dau
int n=0;
for(NODE* k=l.pHead; k!=NULL; k=k->pNext){
    n++;// tim so luong node
}
if(l.pHead==NULL && vt==1){
    themvaodau(l, p);
}
//them vao cuoi
else if(vt == n+1){
    themvaocuoi(l, p);
}
else{
    //them vao giua
    NODE* q= l.pHead;
    int dem=1;
    while(q!= NULL && dem<n-1){
        q=q->pNext;
        dem++;
    }
    //neu vtri khong hop le
    if(q==NULL){
        cout<<"vi tri khong hop le"<<endl;
        return;;
    }
    p->pNext=q->pNext;
    q->pNext=p;
}
}

int main() {
    LIST l;
    KhoiTao(l);

    // Thêm vài node ban đầu
    themvaocuoi(l, KhoiTaoNode(10));
    themvaocuoi(l, KhoiTaoNode(20));
    themvaocuoi(l, KhoiTaoNode(40));

    cout << "\n Danh sach ban dau: ";
    Xuatdanhsach(l);

    NODE* p = KhoiTaoNode(30);
    ThemVaoBatKy(l, p, 3);  // chèn 30 vào vị trí 3

    cout << "\n Danh sach sau khi chen 30 vao vi tri 3: ";
    Xuatdanhsach(l);

    return 0;
}
