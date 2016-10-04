.PHONY: clean-pyc clean-build docs clean

help:
	@echo "docs - generate Sphinx HTML documentation, including API docs"

master:
	git clone -b master `git config --get remote.origin.url` master

docs: master
	cd master && git pull origin master && make docs
	rm -fr _modules _static _sources modules static sources
	mv master/docs/_build/html/* .
	mv _modules modules
	mv _static static
	mv _sources sources
	perl -pi.bak -e 's/_sources/sources/g; s/_static/static/g; s/_modules/modules/g' *.html modules/*.html modules/*/*.html
	rm *.html.bak modules/*.html.bak modules/*/*.html.bak

clean:
	rm *.html
	rm -fr modules static sources

realclean:
	rm -fr master

