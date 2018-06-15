#include <stdint.h>
#include <limits>
#include <iostream>

int main(int argc, char** argv)
{
    std::cout << "MAXINT32 :" << std::numeric_limits<std::int32_t>::max() << std::endl;
    std::uint32_t count = 0;
    std::int32_t i = std::numeric_limits<std::int32_t>::min();
    while (i++ != std::numeric_limits<std::int32_t>::max())
    {
        if (std::abs(i) == i)
            count += 1;
    }

    if (std::abs(i) == i)
        count += 1;

    std::cout << "count :" << count << std::endl;
    return 0;
}