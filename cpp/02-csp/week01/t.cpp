#include <stdio.h>
#include <string.h>
int main(){
    char s[15];
    scanf("%s",s);
    int a=(s[0]==65);
    int value=0;
    for(int i=2;i<strlen(s)-1;i++){
        if(s[i]=='C'){
            value+=1;
        }
    }
    int b=(value==1);
    if(a+b!=2){
        printf("WA");
    }else{
        int index;
        for(int i=2;i<strlen(s);i++){
            if(s[i]=='C'){
                index=i;
        }
    }
    int c=0,d=0;
        for(int i=1;i<index;i++){
            if(s[i]<97){
                c+=1;
                break;
            }
        }
        for(int i=index+1;i<strlen(s);i++){
            if(s[i]<97){
                d+=1;
                break;
            }
        }
        if(c+d!=0){
            printf("WA");
        }else{
            printf("AC");
        }

}
    return 0;
}