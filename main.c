#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <termios.h>
#include <fcntl.h>
#include <ctype.h>
#include "version.h"

static struct termios orig_termios;

void reset_terminal_mode() {
	tcsetattr(STDIN_FILENO, TCSANOW, &orig_termios);
}

void set_nonblocking_terminal_mode() {
	struct termios new_termios;

	// Uložit původní nastavení a zaregistrovat obnovení
	tcgetattr(STDIN_FILENO, &orig_termios);
	atexit(reset_terminal_mode);

	new_termios = orig_termios;

	new_termios.c_lflag &= ~(ICANON | ECHO); // vypnout kanonický režim a echo
	new_termios.c_cc[VMIN] = 0;
	new_termios.c_cc[VTIME] = 0;

	tcsetattr(STDIN_FILENO, TCSANOW, &new_termios);

	// Nastavit stdin na neblokující režim
	fcntl(STDIN_FILENO, F_SETFL, O_NONBLOCK);
}

//extern "C" {
	extern void my_setup();
	extern void my_loop();

	char read_char() {
		char c;
		ssize_t n = read(STDIN_FILENO, &c, 1);
		if (n > 0) {
			return c;
		}
		return 0;
	}

	void write_char(char c) {
		putchar(c);
		fflush(stdout);
	}

	void write_charA(char c) {
		putchar(c < ' ' ? '.' : c);
		fflush(stdout);
	}
//}

void setup() {
	set_nonblocking_terminal_mode();

	printf("1234567890.\n");
	printf("%s\n", VERSION_STRING);
	printf("  based on %s - %s\n", VERSION_COMMIT, VERSION_MESSAGE);
	printf("---- ==== #### FORTH #### ==== ----\n");
	printf("Hint: 0 nodebug 0 noinfo 0 notrace LAST D@ 20 + dump\n");
	printf("Hint: hex ff DDRF !C aa PORTF !C ff DDRK !C aa PORTK !C : x ff  PINF !C ff  PINK !C ; x \n");
	printf(": count- 0 BEGIN DUP c2C PORTF !C PORTK !C 1- DUP ==0 UNTIL c2C PORTF !C PORTK !C ;\n");
	printf(": count+ 0 BEGIN DUP c2C PORTF !C PORTK !C 1 + DUP ==0 UNTIL c2C PORTF !C PORTK !C ;\n");
	printf("Test: : xx 0BRANCH [ 0 3 , ] 5 ; : xxx IF 1111 ELSE 2222 FI 3333 + ;\n");

	my_setup();
	printf("Setup done\n");
	fflush(stdout);
}

void loop() {
	char c = read_char();
	if (c) {
		write_char(c);  // echo
	}
	my_loop();
}
int main() {
	setup();
//	while(1) loop();
}
