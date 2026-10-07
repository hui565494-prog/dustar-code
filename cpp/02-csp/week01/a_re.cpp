#include <stdio.h>

int main(){
    int x;
    scanf("%d",&x);
    int out=0;
    while(x>0){
        if(x%10==1){
            out++;
        }
        x/=10;
    }
    printf("%d",out);
    return 0;
}