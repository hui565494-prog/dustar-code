#include <stdio.h>

int main(){
    int x;
    scanf("%d",&x);
    char a[4]="ABC";
    char b[4]="ARC";
    char c[4]="AGC";

    if(x<1200){
        printf("%s",a);
    }else if(x<2800){
        printf("%s",b);
    }else{
        printf("%s",c);
    }
    return 0;
}