#include <iostream>
#include <string>

int main()
{
    int first;
    int second;
    int third;

    std::cout << "第一个整数:";
    std::cin >> first;

    std::cout << "第二个整数:";
    std::cin >> second;

    std::cout << "第三个整数:";
    std::cin >> third;

    int sum = first + second + third;
    double average = sum / 3.0;

    std::cout << "和为" << sum << std::endl << "平均值为" << average << std::endl;

    return 0;
}