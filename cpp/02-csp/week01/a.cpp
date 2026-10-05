#include <stdio.h>

int main(){
    int x;
    int out=0;
    scanf("%d",&x);
        if(x>=100){
            out++;
            x=x-100;
        }
        if(x>=10){
            out++;
            x=x-10;
        }
        if(x==1){
            out++;
        }
    printf("%d",out);
    return 0;
}