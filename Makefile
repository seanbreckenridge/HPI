.DEFAULT_GOAL := install
BASH=$(/usr/bin/env bash)

install:
	$(BASH) ./scripts/install

lint:
	$(BASH) ./scripts/lint
