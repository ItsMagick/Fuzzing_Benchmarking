# Define variables
CC = gcc
CFLAGS = -shared -fPIC -ldl -pthread
TARGET = preload_redirect.so
SRC = std_out_redirect.c

# Default target
all: $(TARGET)

# Rule to build the shared library
$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $@ $<

# Clean rule
clean:
	rm -f $(TARGET)
