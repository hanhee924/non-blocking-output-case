all:
	g++ -std=c++17 -Wall -o sample sample.cpp

clean:
	rm -f sample

run: all
	./sample

.PHONY: all clean run