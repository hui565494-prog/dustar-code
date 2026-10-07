#include <stdio.h>

int main(){
    int a,b,x;
    scanf("%d%d%d",&a,&b,&x);
    if(x<a){
        printf("NO");
    }else{
        if(x-a>b){
            printf("NO");        
        }else{
            printf("YES");       
        }
    }
}