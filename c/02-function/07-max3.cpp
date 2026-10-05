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
int max3(int a, int b, int c)
{
    int cache = max2(a, b);
    return max2(cache, c);
}

int main()
{
    int a, b, c;
    scanf("%d %d %d", &a, &b, &c);
    int output = max3(a, b, c);
    printf("%d", output);
    return 0;
}