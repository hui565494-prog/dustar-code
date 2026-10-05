#include <stdio.h>

int main()
{
    int a, b;
    scanf("%d %d", &a, &b);
    printf("商: %d\n", a / b);
    printf("余数: %d\n", a % b);
    printf("精确商: %.2lf\n", (double)a / b);
    return 0;
}