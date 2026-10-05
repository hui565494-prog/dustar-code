#include <stdio.h>

int main()
{
    int input;
    scanf("%d", &input);
    if (input % 2)
    {
        printf("奇数");
    }
    else
    {
        printf("偶数");
    }
    return 0;
}