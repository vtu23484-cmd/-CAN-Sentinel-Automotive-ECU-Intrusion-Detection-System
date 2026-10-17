
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdint.h>
#include <time.h>
#include <errno.h>

#include <sys/socket.h>
#include <sys/ioctl.h>
#include <net/if.h>

#include <linux/can.h>
#include <linux/can/raw.h>

int main(void)
{
    int sock;
    struct sockaddr_can addr;
    struct ifreq ifr;
    struct can_frame frame;

    const char *interface_name = "vcan0";

    /* Open a raw CAN socket */
    sock = socket(PF_CAN, SOCK_RAW, CAN_RAW);

    if (sock < 0) {
        perror("Socket creation failed");
        return 1;
    }

    /* Find the virtual CAN interface */
    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, interface_name, IFNAMSIZ - 1);

    if (ioctl(sock, SIOCGIFINDEX, &ifr) < 0) {
        perror("Could not find vcan0");
        close(sock);
        return 1;
    }

    /* Bind the socket to vcan0 */
    memset(&addr, 0, sizeof(addr));
    addr.can_family = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;

    if (bind(sock, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("CAN bind failed");
        close(sock);
        return 1;
    }

    /* Standard CAN identifier for the simulated steering ECU */
    frame.can_id = 0x101;
    frame.can_dlc = 2;

    int steering_angle = -30;

    printf("Steering ECU started on %s\n", interface_name);
    printf("Press Ctrl+C to stop.\n");

    while (1) {
        /* Cycle the simulated steering angle from -30 to +30 */
        steering_angle += 5;

        if (steering_angle > 30) {
            steering_angle = -30;
        }

        /*
         * Encode the angle as a signed 16-bit integer.
         * The two bytes are sent in big-endian order.
         */
        int16_t angle = (int16_t)steering_angle;
        uint16_t raw_angle = (uint16_t)angle;

        frame.data[0] = (raw_angle >> 8) & 0xFF;
        frame.data[1] = raw_angle & 0xFF;

        if (write(sock, &frame, sizeof(frame)) != sizeof(frame)) {
            perror("Failed to send steering frame");
            break;
        }

        printf("Steering angle: %d degrees | CAN ID: 0x101 | Data: %02X %02X\n",
               steering_angle,
               frame.data[0],
               frame.data[1]);

        usleep(200000);
    }

    close(sock);
    return 0;
}
