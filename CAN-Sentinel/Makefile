CC := gcc
CFLAGS := -O2 -Wall -Wextra -Wpedantic

.PHONY: all clean
all: build/can_sniffer

build/can_sniffer: c/can_sniffer.c
	mkdir -p build
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -rf build
