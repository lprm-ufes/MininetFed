FEDERATED = federated/*.py
MN = bin/mn
PYTHON ?= python
PYSRC = $(FEDERATED)
PREFIX ?= /usr

CFLAGS += -Wall -Wextra


install:
	$(PYTHON) setup.py install