#include <stdio.h>

int main()
{
    int n, x;
    int index = 0;
    int a[100], b[100];
    scanf("%d", &n);
    for (int i = 0; i < n; i++)
    {
        scanf("%d", &a[i]);
    }
    scanf("%d", &x);

    for (int i = 0; i < n; i++)
    {
        if (x == a[i])
        {
            b[index] = i;
            index++;
        }
    }
    if (index == 0)
    {
        printf("-1");
    }
    else
    {
        for (int i = 0; i < index; i++)
        {
            printf("%d ", b[i]);
        }
    }
    printf("\n");
    return 0;
}