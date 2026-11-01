#define _GNU_SOURCE
#include <errno.h>
#include <linux/can.h>
#include <linux/can/raw.h>
#include <net/if.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <time.h>
#include <unistd.h>

static volatile sig_atomic_t running = 1;
static void stop_handler(int sig) { (void)sig; running = 0; }

static double epoch_seconds(void) {
    struct timespec ts;
    if (clock_gettime(CLOCK_REALTIME, &ts) != 0) return 0.0;
    return (double)ts.tv_sec + (double)ts.tv_nsec / 1e9;
}

int main(int argc, char **argv) {
    const char *ifname = argc > 1 ? argv[1] : "vcan0";
    int s = socket(PF_CAN, SOCK_RAW, CAN_RAW);
    if (s < 0) { perror("socket(PF_CAN)"); return 1; }

    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    if (strlen(ifname) >= IFNAMSIZ) { fprintf(stderr, "Interface name too long\n"); close(s); return 1; }
    strcpy(ifr.ifr_name, ifname);
    if (ioctl(s, SIOCGIFINDEX, &ifr) < 0) { perror("SIOCGIFINDEX"); close(s); return 1; }

    struct sockaddr_can addr;
    memset(&addr, 0, sizeof(addr));
    addr.can_family = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;
    if (bind(s, (struct sockaddr *)&addr, sizeof(addr)) < 0) { perror("bind CAN socket"); close(s); return 1; }

    signal(SIGINT, stop_handler);
    signal(SIGTERM, stop_handler);
    fprintf(stderr, "CAN-Sentinel C sniffer listening on %s (Ctrl+C to stop)\n", ifname);
    puts("{\"schema\":\"can-sentinel-jsonl-v1\",\"note\":\"following lines are frames\"}");
    fflush(stdout);

    while (running) {
        struct can_frame frame;
        ssize_t n = read(s, &frame, sizeof(frame));
        if (n < 0) {
            if (errno == EINTR) continue;
            perror("read CAN frame"); break;
        }
        if ((size_t)n < sizeof(struct can_frame)) continue;
        unsigned int can_id = frame.can_id & CAN_EFF_MASK;
        printf("{\"timestamp\":%.6f,\"interface\":\"%s\",\"can_id\":%u,\"can_id_hex\":\"%03X\",\"dlc\":%u,\"data\":\"",
               epoch_seconds(), ifname, can_id, can_id, frame.can_dlc);
        for (unsigned int i = 0; i < frame.can_dlc && i < CAN_MAX_DLEN; i++) printf("%02X", frame.data[i]);
        puts("\"}");
        fflush(stdout);
    }
    close(s);
    return 0;
}
