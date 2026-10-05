#include <stdio.h>
int main()
{
    int n;
    scanf("%d", &n);
    int a[n][n];
    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < n; j++)
        {
            scanf("%d", &a[i][j]);
        }
    }
    int max = a[0][0];
    int max_i = 0;
    int max_j = 0;
    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < n; j++)
        {
            if (max < a[i][j])
            {
                max = a[i][j];
                max_i = i;
                max_j = j;
            }
        }
    }
    int x = 0, y = 0;
    for (int i = 0; i < n; i++)
    {
        x = x + a[i][i];
        y = y + a[i][n - 1 - i];
    }
    printf("%d %d\n", x, y);
    printf("%d %d %d", max, max_i, max_j);
    return 0;
}