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
void row_max(int a[][5], int rows)
{
    int out[rows];
    for (int i = 0; i < rows; i++)
    {
        out[i] = a[i][0];
        for (int j = 1; j < 5; j++)
        {
            out[i] = max2(out[i], a[i][j]);
        }
    }
    for (int i = 0; i < rows; i++)
    {
        printf("%d\n", out[i]);
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
    row_max(a, rows);
}