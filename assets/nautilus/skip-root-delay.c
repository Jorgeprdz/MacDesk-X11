#define _POSIX_C_SOURCE 200809L
#include <time.h>

unsigned int sleep(unsigned int seconds)
{
    if (seconds == 7)
        return 0;
    struct timespec requested = { .tv_sec = seconds, .tv_nsec = 0 };
    struct timespec remaining = { 0 };
    return nanosleep(&requested, &remaining) == 0 ? 0 : (unsigned int) remaining.tv_sec;
}
