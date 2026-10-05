#include <stdio.h>

int main()
{
    int n, min, first, index;
    int a[100];
    scanf("%d", &n);
    for (int i = 0; i < n; i++)
    {
        scanf("%d", &a[i]);
    }
    for (int j = 0; j < n; j++)
    {
        first = a[j];
        min = a[j];
        index = j;
        for (int k = j + 1; k < n; k++)
        {
            if (min > a[k])
            {
                min = a[k];
                index = k;
            }
        }
        a[j] = min;
        a[index] = first;
    }
    for (int m = 0; m < n; m++)
    {
        printf("%d ", a[m]);
    }
    printf("\n");
    return 0;
}