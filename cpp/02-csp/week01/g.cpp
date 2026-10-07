#include <stdio.h>

int main(){
    int n;
    scanf("%d",&n);
    int a[105];
    for(int i=0;i<n;i++){
        scanf("%d",&a[i]);
    }

    for(int i=0;i<n;i++){
        int max=a[i];
        int index=i;
        for(int j=i+1;j<n;j++)
        if(max<a[j]){
            max=a[j];
            index=j;
        }
        a[index]=a[i];        
        a[i]=max;
    }
    int out=n;
    if(n==1){
        out=1;
    }else{
        for(int i=0;i<n-1;i++){
            if(a[i]==a[i+1]){
                out-=1;
            }
        }
}
    printf("%d",out);
    return 0;
}