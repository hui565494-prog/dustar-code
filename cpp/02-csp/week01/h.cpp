#include <stdio.h>

int main(){
    int x,a,b;
    scanf("%d%d%d",&x,&a,&b);
    x-=a;
    int value=x/b;
    x-=value*b;
    printf("%d",x);
    return 0;
}