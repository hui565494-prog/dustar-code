#include <stdio.h>
int sum(int a,int b,int c){
    return 10000*a+1000*b+100*c+10*b+a;
}
int main(){
    int low,high;
    scanf("%d%d",&low,&high);
    int a,b;
    a=high/10000-low/10000;
    b=low/10000;
    int out=0;
    for(int i=0;i<=a;i++){
        for(int j=0;j<10;j++){
            for(int k=0;k<10;k++){
                    if(low<=sum(i+b,j,k) && sum(i+b,j,k)<=high){
                        out+=1;
                    }
            }
        }
    }
    printf("%d",out);
    return 0;
}