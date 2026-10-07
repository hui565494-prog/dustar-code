#include <stdio.h>

int main(){
    char s[5];
    scanf("%s",s);
    int sum=0;
    for(int i=0;i<3;i++){
        if('a'==s[i]){
            sum++;
            break;
        }            
    }
    for(int i=0;i<3;i++){
        if('b'==s[i]){
            sum++;
            break;
        }               
    }
    for(int i=0;i<3;i++){
        if('c'==s[i]){
            sum++;
            break;
        }                 
    }
    if(sum==3){
        printf("Yes");
    }else{
        printf("No");
    }
}