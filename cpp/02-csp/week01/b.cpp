#include <stdio.h>

int main(){
    int n;
    scanf("%d",&n);
    int a[205];
    for(int i=0;i<n;i++){
        scanf("%d",&a[i]);
    }
    int times=0;
    while(true){
        for(int i=0;i<n;i++){
            if(a[i]%2!=0){
                goto end;
            }else{
                a[i]/=2;
            }
        }
        times++;
    }
    end:printf("%d",times);
    return 0;
}