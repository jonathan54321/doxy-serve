#pragma once
#include <cstdio>

class IDemo 
{
    public:
    virtual void print() = 0;
};

class DemoB: public IDemo
{
    public:
    void print() override;
};