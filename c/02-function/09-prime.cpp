#include <stdio.h>
int divisible(int a, int b)
{
    return ((a / b) == ((double)a / b));
}
void isPrime(int n)
{
    if (n < 2)
    {
        printf("no\n");
        return;
    }
    else
    {

        int i = 2;
        while (i * i <= n)
        {
            if (divisible(n, i))
            {
                printf("no\n");
                break;
            }
            else
            {
                i++;
            }
        }
        if (i * i > n)
        {
            printf("yes\n");
        }
    }
}

int main()
{
    int x;
    scanf("%d", &x);
    isPrime(x);
    return 0;
}