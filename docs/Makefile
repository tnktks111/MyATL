SPHINXBUILD ?= python -m sphinx
SOURCEDIR = .
BUILDDIR = _build

.PHONY: help html doctest clean

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)"

html:
	@$(SPHINXBUILD) -W -b html "$(SOURCEDIR)" "$(BUILDDIR)/html"

doctest:
	@$(SPHINXBUILD) -W -b doctest "$(SOURCEDIR)" "$(BUILDDIR)/doctest"

clean:
	@$(SPHINXBUILD) -M clean "$(SOURCEDIR)" "$(BUILDDIR)"
