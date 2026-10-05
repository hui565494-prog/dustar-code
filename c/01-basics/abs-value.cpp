#include <stdio.h>

int main()
{
    int n, value;
    scanf("%d", &n);
    value = n < 0;
    printf("%d", n * (1 - 2 * value));
    return 0;
}