#include <stdio.h>

int main()
{
    int n, now, next;
    int sum;
    scanf("%d", &n);
    scanf("%d", &now);
    sum = now;
    for (int i = 1; i < n; i++)
    {
        scanf("%d", &next);
        sum += next;
        if (next > now)
        {
            now = next;
        }
    }
    printf("sum=%d\n", sum);
    printf("max=%d\n", now);
    return 0;
}