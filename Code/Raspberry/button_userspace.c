#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <signal.h>
#include <sys/ioctl.h>

#define SIG_RUN 20
#define INIT_WATCHDOG 0x65

int bm;
int err;

//Detects incoming signal
void signalHandler(int signal) {
    if (signal == SIG_RUN) {
        printf("BUTTON USERSPACE: RECEIVED RUN SIGNAL");
    }

    // Open the command for reading.
    FILE *script;
    script = popen("python3 WatchDog.py", "r");

    if (script == NULL) {
        printf("USERSPACE: WATCHDOG COULD NOT BE RAN\n" );
        exit(1);
    }

    err = pclose(script);

    if (err < 0){
        printf("BUTTON USERSPACE: ERROR\n");
    } else {
        printf("BUTTON USERSPACE: WAITING\n");
    }
}

int main(int argc, char *argv[]) {
    signal(SIG_RUN, signalHandler);

    bm = open("/dev/irq_signal", O_RDONLY);
    if (bm < 0) {
        perror("BUTTON USERSPACE: FAILED TO READ DRIVER\n");
        return -1;
    }

    err = ioctl(bm, INIT_WATCHDOG, NULL);
    if(err < 0) {
		perror("BUTTON USERSPACE: ERROR PROVIDING PID\n");
		close(bm);
		return -1;
	}
    
    // Wait for Signal
	printf("BUTTON USERSPACE: WAITING\n");
	while(1)
		sleep(1);
}