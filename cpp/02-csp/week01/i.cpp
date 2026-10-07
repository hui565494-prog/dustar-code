#include <stdio.h>

int sum(int a, int b, int c, int x)
{
    return (500 * a + 100 * b + 50 * c == x);
}

int main()
{
    int a, b, c, x;
    scanf("%d%d%d%d", &a, &b, &c, &x);
    int out = 0;
    for (int i = 0; i <= a; i++)
    {
        if (500 * i > x)
        {
            break;
        }
        else
        {
            for (int j = 0; j <= b; j++)
            {
                if (j * 100 > x)
                {
                    break;
                }
                else
                {
                    for (int k = 0; k <= c; k++)
                    {
                        if (k * 50 > x)
                        {
                            break;
                        }
                        else
                        {
                            out += sum(i, j, k, x);
                        }
                    }
                }
            }
        }
    }
    printf("%d", out);
    return 0;
}