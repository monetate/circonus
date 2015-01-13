COVERAGE  := coverage
PIP       := pip
PYTHON    := python
RM        := rm
RM_FLAGS  := -rf
SETUP     := setup.py

build_dir := build
dist_dir  := dist

help:
	@$(MAKE) --print-data-base --question no-such-target | \
	grep -v -e '^no-such-target' -e '^Makefile'	     | \
	awk '/^[^.%][-A-Za-z0-9_]*:/ \
	     { print substr($$1, 1, length($$1)-1) }'        | \
	sort					             | \
	pr -2 -t

init:
	$(PIP) install -r requirements.txt

test:
	$(COVERAGE) run --source=circonus test_circonus.py

coverage: test
	$(COVERAGE) report -m

register:
	$(PYTHON) $(SETUP) register

source:
	$(PYTHON) $(SETUP) sdist

egg:
	$(PYTHON) $(SETUP) bdist_egg

upload:
	$(PYTHON) $(SETUP) sdist bdist_egg upload

clean:
	rm -rf $(build_dir) $(dist_dir) *.egg-info

.PHONY: help init test register source egg upload clean
