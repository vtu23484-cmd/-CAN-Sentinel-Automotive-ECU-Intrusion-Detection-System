/*
 * CAN-Sentinel Week 2 - safe, lab-only SocketCAN traffic injection.
 * This program is intentionally locked to Linux vcan0 (a virtual interface).
 * It cannot select any physical CAN adapter or alter vehicle hardware.
 * Default: spoof the Week 1 Steering ECU ID 0x101 at 60 frames/sec.
 * The payload 7F FF is a synthetic out-of-range steering value.
 */
#define _DEFAULT_SOURCE
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <inttypes.h>
#include <linux/can.h>
#include <linux/can/raw.h>
#include <net/if.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <time.h>
#include <unistd.h>

static void help(const char *name) {
    fprintf(stderr, "Usage: %s [--seconds 8] [--rate 60] [--id 101|102|130]\n", name);
    fprintf(stderr, "Only vcan0 is supported. IDs are hexadecimal without 0x.\n");
}
static long positive(const char *value, long min, long max) {
    char *end = NULL;
    errno = 0;
    long n = strtol(value, &end, 10);
    if (errno || !end || *end || n < min || n > max) return -1;
    return n;
}
static double now_seconds(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return (double)t.tv_sec + (double)t.tv_nsec / 1e9;
}
int main(int argc, char **argv) {
    long duration = 8, rate = 60;
    unsigned int id = 0x101;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--help")) { help(argv[0]); return 0; }
        if (i + 1 >= argc) { help(argv[0]); return 2; }
        if (!strcmp(argv[i], "--seconds")) duration = positive(argv[++i], 1, 120);
        else if (!strcmp(argv[i], "--rate")) rate = positive(argv[++i], 1, 500);
        else if (!strcmp(argv[i], "--id")) {
            const char *option = argv[++i];
            if (!strcmp(option, "101")) id = 0x101;
            else if (!strcmp(option, "102")) id = 0x102;
            else if (!strcmp(option, "130")) id = 0x130;
            else { fprintf(stderr, "Only lab IDs 101, 102 and 130 are allowed.\n"); return 2; }
        } else { help(argv[0]); return 2; }
        if (duration < 0 || rate < 0) { help(argv[0]); return 2; }
    }
    int sock = socket(PF_CAN, SOCK_RAW, CAN_RAW);
    if (sock < 0) { perror("CAN socket"); return 1; }
    struct ifreq ifr = {0};
    strncpy(ifr.ifr_name, "vcan0", IFNAMSIZ - 1);
    if (ioctl(sock, SIOCGIFINDEX, &ifr) < 0) {
        perror("vcan0 not available (configure the virtual CAN interface first)");
        close(sock); return 1;
    }
    struct sockaddr_can addr = {0};
    addr.can_family = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;
    if (bind(sock, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("Bind vcan0"); close(sock); return 1;
    }
    struct can_frame frame = {0};
    frame.can_id = id;
    frame.can_dlc = 2;
    frame.data[0] = 0x7F;
    frame.data[1] = 0xFF;
    const long requested = duration * rate;
    const double start = now_seconds();
    long sent = 0;
    printf("CAN-Sentinel Week 2 virtual injection: vcan0 ID=%03X rate=%ld/s duration=%lds\n",
           id, rate, duration);
    fflush(stdout);
    for (long i = 0; i < requested; i++) {
        /* Schedule against monotonic time to avoid accumulating drift. */
        double target = start + (double)i / (double)rate;
        double delay = target - now_seconds();
        if (delay > 0) {
            struct timespec wait = { (time_t)delay, (long)((delay - (time_t)delay) * 1e9) };
            while (nanosleep(&wait, &wait) < 0 && errno == EINTR) {}
        }
        ssize_t n = write(sock, &frame, sizeof(frame));
        if (n != (ssize_t)sizeof(frame)) { perror("Send CAN frame"); break; }
        sent++;
    }
    printf("SENT=%ld\n", sent);
    printf("ELAPSED_SECONDS=%.3f\n", now_seconds() - start);
    close(sock);
    return sent == requested ? 0 : 1;
}
