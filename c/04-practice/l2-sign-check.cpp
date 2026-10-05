#include <stdio.h>

int main()
{
    int n;
    scanf("%d", &n);
    if (n < -1000 || n > 1000)
    {
        printf("超出范围\n");
    }
    else if (n == 0)
    {
        printf("零\n");
    }
    else
    {
        int value = n > 0;
        if (value)
        {
            printf("正数\n");
        }
        else
        {
            printf("负数\n");
        }
    }
    return 0;
}