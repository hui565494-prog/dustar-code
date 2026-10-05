#include <stdio.h>

int main()
{
    int x;
    double avg;

    printf("输入数字\n");
    scanf("%d %lf", &x, &avg);
    printf("%d\n%.2lf", x, avg);
    return 0;
}