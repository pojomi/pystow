PREFIX  ?= /usr/local
BINDIR   = $(PREFIX)/bin
LIBDIR   = $(PREFIX)/lib/pystow
PYTHON  ?= python3
NAME     = pystow
SRCS     = pystow.py keymap.py classes.py manage_windows.py hex_to_rgb.py

.PHONY: all compile install uninstall clean

all: compile

compile:
	$(PYTHON) -m compileall -q $(SRCS)

install: compile
	install -d $(DESTDIR)$(LIBDIR)
	install -m644 $(SRCS) $(DESTDIR)$(LIBDIR)
	cp -r __pycache__ $(DESTDIR)$(LIBDIR)/
	install -d $(DESTDIR)$(BINDIR)
	printf '#!/bin/sh\nexec $(PYTHON) $(LIBDIR)/pystow.py "$$@"\n' \
		> $(DESTDIR)$(BINDIR)/$(NAME)
	chmod 755 $(DESTDIR)$(BINDIR)/$(NAME)

uninstall:
	rm -f $(DESTDIR)$(BINDIR)/$(NAME)
	rm -rf $(DESTDIR)$(LIBDIR)

clean:
	rm -rf __pycache__
