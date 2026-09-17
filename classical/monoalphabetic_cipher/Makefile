CXX ?= c++
CXXFLAGS ?= -std=c++17 -Wall -Wextra -pedantic -O2

TARGET := monoalphabetic_cipher
SOURCES := main.cpp monoalphabetic_cipher.cpp

$(TARGET): $(SOURCES) monoalphabetic_cipher.h
	$(CXX) $(CXXFLAGS) $(SOURCES) -o $(TARGET)

.PHONY: clean
clean:
	rm -f $(TARGET)
