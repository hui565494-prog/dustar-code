#include <stdio.h>

int fact(int n)
{
    if (n <= 1)
    {
        return 1;
    }
    return n * fact(n - 1);
}
int C(int n, int m)
{
    return fact(n) / (fact(m) * fact(n - m));
}
int main()
{
    int m, n;
    scanf("%d %d", &n, &m);
    int result_1 = fact(n);
    int result_2 = fact(m);
    int result_3 = C(n, m);
    printf("%d %d\n%d\n", result_1, result_2, result_3);
    return 0;
}