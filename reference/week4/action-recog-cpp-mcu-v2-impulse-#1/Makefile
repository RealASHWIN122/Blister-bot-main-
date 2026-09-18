CC=g++
CFLAGS=-Wall -O3 -I. -Iedge-impulse-sdk -Imodel-parameters -Itflite-model
LDFLAGS=-lm -lstdc++ -pthread

SOURCES := model_server.cpp \
           $(wildcard edge-impulse-sdk/porting/posix/*.c*) \
           $(wildcard edge-impulse-sdk/porting/posix/*.cpp) \
           $(wildcard edge-impulse-sdk/dsp/kissfft/*.cpp) \
           $(wildcard edge-impulse-sdk/dsp/dct/*.cpp) \
           $(wildcard edge-impulse-sdk/dsp/memory.cpp) \
           $(wildcard tflite-model/*.cpp) \
           $(wildcard tflite-model/tflite-model/*.cpp)

all:
	$(CC) $(CFLAGS) $(SOURCES) $(LDFLAGS) -o model_server

clean:
	rm -f model_server
