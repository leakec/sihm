DIRS = $(wildcard */)
DIRS2 = $(wildcard */)

.PHONY: docs $(DIRS) clean $(DIRS2)
docs: $(DIRS)
clean: $(DIRS2)

$(DIRS):
	$(MAKE) -C $@ docs

$(DIRS2):
	$(MAKE) -C $@ clean
