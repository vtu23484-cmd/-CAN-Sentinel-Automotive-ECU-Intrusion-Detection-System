
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>

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

    /* Create a raw CAN socket */
    sock = socket(PF_CAN, SOCK_RAW, CAN_RAW);

    if (sock < 0) {
        perror("Socket creation failed");
        return 1;
    }

    /* Obtain the index of vcan0 */
    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, interface_name, IFNAMSIZ - 1);

    if (ioctl(sock, SIOCGIFINDEX, &ifr) < 0) {
        perror("Could not find vcan0");
        close(sock);
        return 1;
    }

    /* Bind the socket to the virtual CAN interface */
    memset(&addr, 0, sizeof(addr));
    addr.can_family = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;

    if (bind(sock, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("CAN bind failed");
        close(sock);
        return 1;
    }

    /* Standard CAN ID for the simulated RPM ECU */
    frame.can_id = 0x102;
    frame.can_dlc = 2;

    int rpm = 800;

    printf("RPM ECU started on %s\n", interface_name);
    printf("CAN ID: 0x102 | Press Ctrl+C to stop.\n");

    while (1) {
        /* Simulate engine RPM between 800 and 3000 */
        rpm += 200;

        if (rpm > 3000) {
            rpm = 800;
        }

        /*
         * Encode RPM as an unsigned 16-bit integer.
         * Send the most significant byte first.
         */
        uint16_t raw_rpm = (uint16_t)rpm;

        frame.data[0] = (raw_rpm >> 8) & 0xFF;
        frame.data[1] = raw_rpm & 0xFF;

        if (write(sock, &frame, sizeof(frame)) != sizeof(frame)) {
            perror("Failed to send RPM frame");
            break;
        }

        printf("Engine RPM: %d | CAN ID: 0x102 | Data: %02X %02X\n",
               rpm, frame.data[0], frame.data[1]);

        usleep(500000);
    }

    close(sock);
    return 0;
}
