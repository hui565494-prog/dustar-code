#include <stdio.h>
int max2(int a,int b){
    if(a>b){
        return a;
    }else{
        return b;
    }
}
int main(){
    int a,b;
    scanf("%d%d",&a,&b);
    int c=max2(a+b,a-b);
    int out=max2(c,a*b);
    printf("%d",out);
    return 0;
}