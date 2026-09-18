#include <iostream>
#include <vector>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <cstring>
#include <thread>

#include "edge-impulse-sdk/classifier/ei_run_classifier.h"

#define PORT 9999
#define BUFFER_SIZE (EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE * 3) // 96 * 96 * 3

// Global buffer for features
std::vector<float> features;

void handle_client(int client_socket) {
    uint8_t buffer[BUFFER_SIZE];
    
    while (true) {
        int bytes_read = 0;
        // Read exactly BUFFER_SIZE bytes (one full frame)
        while (bytes_read < BUFFER_SIZE) {
            int result = read(client_socket, buffer + bytes_read, BUFFER_SIZE - bytes_read);
            if (result <= 0) {
                std::cerr << "Client disconnected or error reading." << std::endl;
                close(client_socket);
                return;
            }
            bytes_read += result;
        }

        // Convert raw RGB bytes to Edge Impulse format (0xRRGGBB)
        features.clear();
        for (int i = 0; i < BUFFER_SIZE; i += 3) {
            uint32_t r = buffer[i];
            uint32_t g = buffer[i+1];
            uint32_t b = buffer[i+2];
            uint32_t hex_value = (r << 16) | (g << 8) | b;
            features.push_back(static_cast<float>(hex_value));
        }

        // Construct the signal
        signal_t signal;
        int err = numpy::signal_from_buffer(features.data(), features.size(), &signal);
        if (err != 0) {
            std::string err_msg = "ERR: Signal\n";
            send(client_socket, err_msg.c_str(), err_msg.length(), 0);
            continue;
        }

        // Run classifier
        ei_impulse_result_t result = { 0 };
        EI_IMPULSE_ERROR res = run_classifier(&signal, &result, false);

        if (res != 0) {
            std::string err_msg = "ERR: Classifier\n";
            send(client_socket, err_msg.c_str(), err_msg.length(), 0);
            continue;
        }

        // Find highest confidence label
        std::string top_label = "unknown";
        float top_value = 0.0f;

        for (size_t ix = 0; ix < EI_CLASSIFIER_LABEL_COUNT; ix++) {
            if (result.classification[ix].value > top_value) {
                top_value = result.classification[ix].value;
                top_label = result.classification[ix].label;
            }
        }

        // Prepare response: LABEL:CONFIDENCE\n
        std::string response = top_label + ":" + std::to_string(top_value) + "\n";
        send(client_socket, response.c_str(), response.length(), 0);
    }
}

int main() {
    int server_fd, client_socket;
    struct sockaddr_in address;
    int opt = 1;
    int addrlen = sizeof(address);

    // Ensure features vector is correctly sized
    features.reserve(EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE);

    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("Socket failed");
        exit(EXIT_FAILURE);
    }

    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt))) {
        perror("setsockopt");
        exit(EXIT_FAILURE);
    }

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("Bind failed");
        exit(EXIT_FAILURE);
    }

    if (listen(server_fd, 3) < 0) {
        perror("Listen");
        exit(EXIT_FAILURE);
    }

    std::cout << "Edge Impulse Model Server listening on port " << PORT << std::endl;

    while (true) {
        if ((client_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen)) < 0) {
            perror("Accept");
            continue;
        }
        std::cout << "Client connected!" << std::endl;
        std::thread client_thread(handle_client, client_socket);
        client_thread.detach();
    }

    return 0;
}
