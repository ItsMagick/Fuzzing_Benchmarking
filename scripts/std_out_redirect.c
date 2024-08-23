#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <unistd.h>
#include <fcntl.h>
#include <pthread.h>
#include <time.h>
#include <string.h>

static int stdout_pipe[2];
static int stderr_pipe[2];
static pthread_t stdout_thread;
static pthread_t stderr_thread;
static FILE *log_file = NULL;

static void* redirect_output(void* arg);
static void get_timestamp(char* buffer, size_t size);

static void __attribute__((constructor)) init(void) {
    // Create pipes for stdout and stderr
    if (pipe(stdout_pipe) == -1) {
        perror("pipe");
        exit(EXIT_FAILURE);
    }
    if (pipe(stderr_pipe) == -1) {
        perror("pipe");
        exit(EXIT_FAILURE);
    }

    // Open the log file
    const char *log_file_path = getenv("LOG_FILE");
    if (!log_file_path) {
        log_file_path = "mqtt_aflnet_stdout.log"; // Default log file if LOG_FILE is not set
    }
    log_file = fopen(log_file_path, "a");
    if (!log_file) {
        perror("fopen");
        exit(EXIT_FAILURE);
    }

    // Redirect stdout and stderr to the write end of the pipes
    if (dup2(stdout_pipe[1], STDOUT_FILENO) == -1) {
        perror("dup2 stdout");
        exit(EXIT_FAILURE);
    }
    if (dup2(stderr_pipe[1], STDERR_FILENO) == -1) {
        perror("dup2 stderr");
        exit(EXIT_FAILURE);
    }

    // Close the original write ends as they're now duplicated
    close(stdout_pipe[1]);
    close(stderr_pipe[1]);

    // Start threads to process the output
    pthread_create(&stdout_thread, NULL, redirect_output, &stdout_pipe[0]);
    pthread_create(&stderr_thread, NULL, redirect_output, &stderr_pipe[0]);

}

static void* redirect_output(void* arg) {
    int pipe_fd = *(int*)arg;
    FILE* stream = fdopen(pipe_fd, "r");
    char buffer[4096];
    char timestamp[20];

    while (fgets(buffer, sizeof(buffer), stream)) {
        get_timestamp(timestamp, sizeof(timestamp));
        fprintf(log_file, "[%s] %s", timestamp, buffer);
        fflush(log_file);  // Ensure it is written immediately
    }

    fclose(stream);
    return NULL;
}

// Helper function to get the current timestamp
static void get_timestamp(char* buffer, size_t size) {
    time_t now = time(NULL);
    struct tm* t = localtime(&now);
    strftime(buffer, size, "%Y-%m-%d %H:%M:%S", t);
}
