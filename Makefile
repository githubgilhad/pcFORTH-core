TARGET := pcFORTH.elf
BUILD_DIR := build-pc

DEFINES+= -DOUTPUT_TARGET=OUTPUT_TARGET_terminal -D__PC__

CC := gcc
CXX := g++
AS := gcc -x assembler-with-cpp

CFLAGS := -O2 -Wall -MMD -I. $(DEFINES)
CXXFLAGS := -O2 -Wall -MMD -I. $(DEFINES)
LDFLAGS :=

# 32bit code
CFLAGS   += -m32 -Os -g
CXXFLAGS += -m32 -Os -g
LDFLAGS  += -m32

LDFLAGS += -no-pie	# asm relokace

SRC_C := $(wildcard *.c)
SRC_CPP := $(wildcard *.cpp)
SRC_S := $(wildcard *.S)

OBJ_C := $(patsubst %.c, $(BUILD_DIR)/%.o, $(SRC_C))
OBJ_CPP := $(patsubst %.cpp, $(BUILD_DIR)/%.o, $(SRC_CPP))
OBJ_S := $(patsubst %.S, $(BUILD_DIR)/%.o, $(SRC_S))

OBJS := $(OBJ_C) $(OBJ_CPP) $(OBJ_S)
DEPS := $(OBJS:.o=.d)

.PHONY: all clean help

all: $(TARGET)

$(TARGET): $(OBJS) Makefile
	$(CXX) $(OBJS) -o $@ $(LDFLAGS)
	objdump --disassemble --source --line-numbers --demangle -z --section=.text  --section=.data --section=.bss -M intel $@ >$@.dis

$(BUILD_DIR)/%.o: %.c Makefile | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD_DIR)/%.o: %.cpp Makefile | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -c $< -o $@

$(BUILD_DIR)/%.o: %.S Makefile | $(BUILD_DIR)
	$(AS) $(CFLAGS) -c $< -o $@

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

# {{{ version
# Makro pro získání dat z gitu
GIT_DESCRIBE := $(shell git describe --tags --long 2>/dev/null || echo "v0.0.0-0-g0000000")
GIT_COMMIT_HASH := $(shell git rev-parse --short HEAD)
GIT_COMMIT_MESSAGE := $(shell git log -1 --pretty=%s)
VERSION_HEADER := version.h

# Cíl pro generování version.h
$(VERSION_HEADER): FORCE
	@echo "Checking version..."
	@TMPFILE=$$(mktemp) && \
	echo "#pragma once" > $$TMPFILE && \
	echo "#define VERSION_STRING \"$(GIT_DESCRIBE)++\"" >> $$TMPFILE && \
	echo "#define VERSION_COMMIT \"$(GIT_COMMIT_HASH)\"" >> $$TMPFILE && \
	echo "#define VERSION_MESSAGE \"$(GIT_COMMIT_MESSAGE)\"" >> $$TMPFILE && \
	if ! cmp -s $$TMPFILE $(VERSION_HEADER); then \
		echo "Updating $(VERSION_HEADER)"; \
		mv $$TMPFILE $(VERSION_HEADER); \
	else \
		echo "$(VERSION_HEADER) is up to date"; \
		rm $$TMPFILE; \
	fi


# Umožní vždy ověřit stav
FORCE:

# Cíl pro návrh nového tagu
new_tag:
	@LAST_TAG=$$(git tag --sort=-v:refname | head -n1); \
	if [ -z "$$LAST_TAG" ]; then \
		NEW_TAG="v0.0.1"; \
	else \
		IFS=. read -r MAJOR MINOR PATCH <<< "$$(echo $$LAST_TAG | sed 's/^v//')"; \
		PATCH=$$((PATCH + 1)); \
		NEW_TAG="v$${MAJOR}.$${MINOR}.$${PATCH}"; \
	fi; \
	echo "Suggested new tag:"; \
	echo "git tag -a $$NEW_TAG -m \"Release $$NEW_TAG\""; \
	echo "git push origin $$NEW_TAG"

# Cíl pro ruční vygenerování nové verze
version: $(VERSION_HEADER)
.PHONY: FORCE new_tag version monitor upload_monitor
# }}}


asm.S: words.inc
words.inc: words.4th
	./forth2inc.py

clean:
	$(RM) -r $(BUILD_DIR) $(TARGET) $(TARGET).dis

help:
	@echo "Jednoduchý Makefile pro překlad *.c/*.cpp/*.S na Linux (x86_64)"
	@echo "Použití:"
	@echo "  make        -> Překlad výchozího cíle ($(TARGET))"
	@echo "  make clean  -> Odstraní build adresář a binárku"
	@echo "  make help   -> Zobrazí tuto nápovědu"
	@echo "Aditional targets:"
	@echo "  make disassm           - disassmbly target"
	@echo "  make version           - make/update version.h"
	@echo "  make new_tag           - suggest new tag for git"

-include $(DEPS)
