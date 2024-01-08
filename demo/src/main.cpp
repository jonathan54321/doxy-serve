#include <array>

#include <demo.h>
#include <demo.hpp>


int main()
{
    auto a {DemoA()};
    auto b {DemoB()};

    std::array<IDemo*,2> demos { &a, &b}; 

    for( auto * d : demos )
    {
        d->print();
    }
    return 0;
}