#include <stdio.h>

int main()
{
    int i;
    for (i = 0; i < 5; i++)
    {
        printf("%d\n", i);
    }
    while (i < 10)
    {
        printf("%d\n", i);
        i++;
    }
    return 0;
}