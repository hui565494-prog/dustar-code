#include <stdio.h>
#include <string.h>


int main(){
    char s[105],t[105];
    scanf("%s%s",s,t);
    int len_s=strlen(s),
        len_t=strlen(t);
    for(int i=0;i<len_s;i++){
        int min=s[i];
        int index=i;
        for(int j=i+1;j<len_s;j++){
            if(min>s[j]){
                min=s[j];
                index=j;
            }
        }
        s[index]=s[i];
        s[i]=min;
    }
    for(int i=0;i<len_t;i++){
        int max=t[i];
        int index=i;
        for(int j=i+1;j<len_t;j++){
            if(max<t[j]){
                max=t[j];
                index=j;
            }
        }
        t[index]=t[i];
        t[i]=max;
    }
    for(int i=0;i<105;i++){
        if(s[i]<t[i]){
            printf("Yes");
            break;
        }else if(s[i]>t[i]){
            printf("No");
            break;
        }else if(s[i]=='\0'&& t[i]=='\0'){
            printf("No");
            break;
        }
    }
    return 0;
}