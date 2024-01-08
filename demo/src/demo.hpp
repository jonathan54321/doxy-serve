#pragma once
#include <demo.h>

class DemoA : public IDemo
{
    public:
    void print() override
    {
        printf("I am a DemoA\n");
    }

};
