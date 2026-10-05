#include <stdio.h>

int main()
{
    int n, target;
    int a[105];
    scanf("%d", &n);
    for (int i = 0; i < n; i++)
    {
        scanf("%d", &a[i]);
    }
    scanf("%d", &target);
    int low, high, mid;
    low = 0, high = n - 1;
    while (high - low > 1)
    {
        mid = (low + high) / 2;
        if (a[mid] == target)
        {
            high = mid;
            break;
        }
        else if (a[mid] < target)
        {
            low = mid;
        }
        else
        {
            high = mid;
        }
    }
    if (a[low] == target)
    {
        printf("%d\n", low);
    }
    else if (a[high] == target)
    {
        printf("%d\n", high);
    }
    else
    {
        printf("-1\n");
    }
    return 0;
}