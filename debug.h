#ifndef DEBUG_H
#define DEBUG_H

#include <stdint.h>
//#include <avr/pgmspace.h>
#include <stdbool.h>
#include "defines.h"
#include "colors.h"
#include "flags.h"
#include "ptr24.h"
#include "io.h"
#define ERROR(X) error(F(X))
#define INFO(X) info(F(X))
#define TRACE(X) trace(F(X))
#define DEBUG_DUMPp(P,LBL) debug_dump(B3U32(P),F(LBL));
#define DEBUG_DUMP(U,LBL) debug_dump(U,F(LBL));

// #define ERROR(X)
// #define INFO(X)
// #define TRACE(X)
// #define DEBUG_DUMPp(P,LBL) 
// #define DEBUG_DUMP(U,LBL) 
void error(const __memx char *c); 
void info(const __memx char *c); 
void trace(const __memx char *c); 
void dump24(uint32_t w, const __memx char *label);
void write_hex8(uint8_t b);
void write_hex16(uint16_t b);
void write_hex24(uint32_t b);
void write_hex32(uint32_t b);
bool is_ram_address(uint32_t addr);
bool is_flash_address(uint32_t addr);
//void debug_dump(const __memx void * address, const __memx char* label);
void debug_dump(uint32_t address, const __memx char* label);
extern bool nodebug;
extern bool noinfo;
extern bool notrace;
#endif
