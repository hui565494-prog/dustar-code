#include <stdio.h>

int main()
{
    int n;
    scanf("%d", &n);
    int a[100];
    for (int i = 0; i < n; i++)
    {
        scanf("%d", &a[i]);
    }
    int first, max, index = 0;
    first = a[0];
    max = a[0];
    for (int j = 1; j < n; j++)
    {
        if (max < a[j])
        {
            max = a[j];
            index = j;
        }
    }
    a[0] = max;
    a[index] = first;
    for (int k = 0; k < n; k++)
    {
        printf("%d ", a[k]);
    }
}