CC = gcc
CFLAGS = -Wall -Wextra -std=c99
LDFLAGS = -lreadline

SRC = ssi.c
TARGET = ssi

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC) $(LDFLAGS)

clean:
	rm -f $(TARGET)

.PHONY: clean