#include <iostream>
#include <string>

int main()
{
    std::cout << "你的名字：";
    std::string name;
    std::cin >> name;

    std::cout << "身高(米):";
    double height;
    std::cin >> height;

    std::cout << "体重(公斤):";
    double weight;
    std::cin >> weight;

    double bmi;
    bmi = weight / (height * height);

    std::cout << name << "的BMI是" << bmi << std::endl;

    return 0;
}