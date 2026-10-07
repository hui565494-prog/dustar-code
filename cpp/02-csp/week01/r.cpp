#include <stdio.h>

void dif(int start,int end,char a[],char b[26]){
    for(int i=0;i<26;i++){
        b[i]=0;
    }

    for(int i=start;i<end;i++){
        b[a[i]-'a']++;
    }
    for(int i=0;i<26;i++){
        if(b[i]!=0){
            b[i]=1;
        }
    }
    return;
}

int max2(int a,int b){
    if(a>b){
        return a;
    }else{
        return b;
    }
}
int main(){
    int n;
    char s[105];
    char a[26];
    char b[26];
    scanf("%d",&n);
    scanf("%s",s);
    int max=0;
    for(int i=1;i<n;i++){
        int cnt=0;
        dif(0,i,s,a);
        dif(i,n,s,b);
        for(int j=0;j<26;j++){
            if(a[j]+b[j]==2){
                cnt+=1;
            }
        }
        max=max2(cnt,max);
    }
    printf("%d",max);
}