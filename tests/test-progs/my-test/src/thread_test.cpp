#include <pthread.h>
#include <stdio.h>

void *thread_routine(void *) {
    printf("Hello from second %llu thread\n",
           (unsigned long long)pthread_self());
    return NULL;
}

int main() {
    pthread_t th;
    pthread_create(&th, NULL, thread_routine, NULL);

    printf("Hello from main %llu thread\n", (unsigned long long)pthread_self());

    pthread_join(th, NULL);

    return 0;
}

