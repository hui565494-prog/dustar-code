#include <stdio.h>

int main()
{
    int n, i, j;
    scanf("%d", &n);
    int a[n];
    for (i = n - 1; i > -1; i--)
    {
        scanf("%d", &a[i]);
    }
    for (j = 0; j < n; j++)
    {
        printf("%d ", a[j]);
    }
    printf("\n");
    return 0;
}