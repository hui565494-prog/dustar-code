#include <iostream>

int main() {
    int mor=0,noon=0,ev=0;
    int mor_pct=0,noon_pct=0,ev_pct=0;
    int total=0,min=0,hour=0;


    std::cout<<"请输入早中晚的学习时长(min)";
    std::cin>>mor>>noon>>ev;

    total=mor+noon+ev;
    hour=total/60;
    min=total-hour*60;

    mor_pct=mor*100/total;
    noon_pct=noon*100/total;
    ev_pct=ev*100/total;

    std::cout<<"总时长："<<hour<<"小时"<<min<<"分钟"<<std::endl<<"早："<<mor_pct<<"% 中："<<noon_pct<<"% 晚："<<ev_pct<<"%"<<std::endl;

    return 0;
}
