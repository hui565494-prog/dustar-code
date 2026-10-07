#include <stdio.h>

int main(){
    int n;
    int a[105];
    scanf("%d",&n);
    for(int i=0;i<n;i++){
        scanf("%d",&a[i]);
    }
    for(int i=0;i<n;i++){
        int max=a[i];
        int index=i;
        for(int j=i+1;j<n;j++){
            if(max<a[j]){
                max=a[j];
                index=j;
            }
        }
        a[index]=a[i];
        a[i]=max;
    }
    int A=0,B=0;
    for(int i=0;i<n;i+=2){
        A+=a[i];
    }
    for(int i=1;i<n;i+=2){
        B+=a[i];
    }   
    int result=A-B;
    printf("%d\n",result);
    return 0;
}