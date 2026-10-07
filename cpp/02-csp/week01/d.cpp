#include <stdio.h>
#include <string.h>


int max2(int a,int b){
    if(a>b){
        return a;
    }else{
        return b;
    }
}

int min2(int a,int b){
    if(a>b){
        return b;
    }else{
        return a;
    }
}
int main(){
    char s[105],t[105];
    scanf("%s",s);
    scanf("%s",t);
    int len_s=strlen(s);
    int len_t=strlen(t);
    int min=s[0];
    int max=t[0];
    for(int i=1;i<len_s;i++){
        max=max2(max,t[i]);
        min=min2(min,s[i]);
    }
    if(min<max){
        printf("Yes");
    }else {
        printf("No");
    }
    return 0;
}