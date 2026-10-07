#include <stdio.h>

int main(){
    int a,b;
    scanf("%d %d",&a,&b);
    int x;
    if((a+b)%2==0){
        x=(a+b)/2;
    }else{
        x=((a+b)/2)+1;
    }
    printf("%d",x);
    return 0;
}