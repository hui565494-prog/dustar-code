#include <stdio.h>

int main(){
    int n,a;
    scanf("%d%d",&n,&a);
    int value=n%500;
    if(value>a){
        printf("No");
    }else{
        printf("Yes");
    }
    return 0;
}