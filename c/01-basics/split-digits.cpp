#include <stdio.h>

int main()
{
    int input, first, second;

    scanf("%d", &input);
    first = input / 10;
    second = input % 10;
    printf("个位：%d\n", second);
    printf("十位：%d\n", first);
    return 0;
}