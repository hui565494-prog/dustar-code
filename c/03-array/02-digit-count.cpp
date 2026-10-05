#include <stdio.h>

int main()
{
    int n, x;
    int cnt[10] = {0};
    scanf("%d", &n);
    for (int i = 0; i < n; i++)
    {
        scanf("%d", &x);
        cnt[x]++;
    }
    for (int j = 0; j < 10; j++)
    {
        printf("%d\n", cnt[j]);
    }
    return 0;
}