#include <stdio.h>
int max2(int a, int b)
{
    if (a > b)
    {
        return a;
    }
    else
    {
        return b;
    }
}
int main()
{
    int rows;
    scanf("%d", &rows);
    int a[rows][5];
    for (int i = 0; i < rows; i++)
    {
        for (int j = 0; j < 5; j++)
        {
            scanf("%d", &a[i][j]);
        }
    }
    for (int i = 0; i < rows; i++)
    {
        int max = a[i][0];
        for (int j = 1; j < 5; j++)
        {
            max = max2(max, a[i][j]);
        }
        printf("%d\n", max);
    }
}