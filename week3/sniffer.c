#define _GNU_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <time.h>
#include <signal.h>

#include <sys/socket.h>
#include <sys/un.h>
#include <sys/ioctl.h>

#include <linux/can.h>
#include <linux/can/raw.h>
#include <net/if.h>

#define SOCKET_PATH "/tmp/can_sentinel.sock"

static volatile sig_atomic_t running = 1;

static void stop_handler(int sig)
{
    (void)sig;
    running = 0;
}

static int send_all(int fd, const char *buffer, size_t length)
{
    size_t sent = 0;

    while (sent < length) {
        ssize_t n = send(fd, buffer + sent, length - sent, MSG_NOSIGNAL);

        if (n < 0) {
            if (errno == EINTR)
                continue;
            return -1;
        }

        if (n == 0)
            return -1;

        sent += (size_t)n;
    }

    return 0;
}

int main(void)
{
    signal(SIGINT, stop_handler);
    signal(SIGTERM, stop_handler);

    /* Open SocketCAN receiver, locked to vcan0. */
    int can_fd = socket(PF_CAN, SOCK_RAW, CAN_RAW);

    if (can_fd < 0) {
        perror("CAN socket");
        return 1;
    }

    struct ifreq ifr = {0};
    strncpy(ifr.ifr_name, "vcan0", IFNAMSIZ - 1);

    if (ioctl(can_fd, SIOCGIFINDEX, &ifr) < 0) {
        perror("vcan0 interface");
        close(can_fd);
        return 1;
    }

    struct sockaddr_can can_addr = {0};
    can_addr.can_family = AF_CAN;
    can_addr.can_ifindex = ifr.ifr_ifindex;

    if (bind(can_fd, (struct sockaddr *)&can_addr,
             sizeof(can_addr)) < 0) {
        perror("Bind vcan0");
        close(can_fd);
        return 1;
    }

    /* Connect to the Python Unix Domain Socket server. */
    int unix_fd = socket(AF_UNIX, SOCK_STREAM, 0);

    if (unix_fd < 0) {
        perror("Unix socket");
        close(can_fd);
        return 1;
    }

    struct sockaddr_un unix_addr = {0};
    unix_addr.sun_family = AF_UNIX;
    strncpy(unix_addr.sun_path, SOCKET_PATH,
            sizeof(unix_addr.sun_path) - 1);

    if (connect(unix_fd, (struct sockaddr *)&unix_addr,
                sizeof(unix_addr)) < 0) {
        perror("Connect to Python server");
        fprintf(stderr, "Start the Python socket server first.\n");
        close(unix_fd);
        close(can_fd);
        return 1;
    }

    printf("CAN Sentinel C sniffer connected to vcan0.\n");
    printf("Forwarding frames to %s\n", SOCKET_PATH);
    fflush(stdout);

    unsigned long long count = 0;

    while (running) {
        struct can_frame frame;

        ssize_t n = read(can_fd, &frame, sizeof(frame));

        if (n < 0) {
            if (errno == EINTR)
                continue;
            perror("CAN read");
            break;
        }

        if (n != sizeof(frame))
            continue;

        if (frame.can_id & CAN_ERR_FLAG)
            continue;

        unsigned int can_id = frame.can_id & CAN_EFF_MASK;
        char payload[3 * CAN_MAX_DLEN + 1] = {0};

        for (int i = 0; i < frame.can_dlc; i++) {
            char byte[4];
            snprintf(byte, sizeof(byte), "%02X%s",
                     frame.data[i],
                     i + 1 < frame.can_dlc ? " " : "");
            strncat(payload, byte, sizeof(payload) - strlen(payload) - 1);
        }

        struct timespec ts;
        clock_gettime(CLOCK_MONOTONIC, &ts);

        double elapsed = ts.tv_sec + ts.tv_nsec / 1e9;

        char message[512];

        int length = snprintf(
            message, sizeof(message),
            "{\"type\":\"frame\",\"timestamp\":%.9f,"
            "\"can_id\":\"%03X\",\"dlc\":%u,\"data\":\"%s\"}\n",
            elapsed, can_id, frame.can_dlc, payload
        );

        if (length <= 0 || (size_t)length >= sizeof(message))
            continue;

        if (send_all(unix_fd, message, (size_t)length) < 0) {
            perror("Unix socket send");
            break;
        }

        count++;

        if (count % 100 == 0) {
            printf("Forwarded %llu CAN frames\n", count);
            fflush(stdout);
        }
    }

    printf("\nSniffer stopped. Total frames: %llu\n", count);

    close(unix_fd);
    close(can_fd);

    return 0;
}
