# Get version from the version.py file
TEMPLATE_SRC_DIR = ../src/sihm/template_project/src
SRC_DIR = ../src
SRC_TS_FILES = $(wildcard $(SRC_DIR)/*.ts)
SRC_JS_FILES = ${subst $(SRC_DIR),$(TEMPLATE_SRC_DIR),${SRC_TS_FILES:.ts=.js}}

VERSION=$(shell cd ../src/sihm; python -c "from version import __version__; print(__version__)")

PYTHON_PKG_FILES=$(shell find $(SRC_DIR))
PYTHON_WHEEL=sihm-$(VERSION)-py3-none-any.whl
PYTHON_WHEEL_DIST=../dist/$(PYTHON_WHEEL)

DEB_PKG=sihm_$(VERSION)-1_all
DEB=../dist/$(DEB_PKG).deb

RPM_PKG=sihm-$(VERSION)-1.noarch.rpm
RPM=../dist/$(RPM_PKG)

BREW=../dist/sihm.rb

../dist:
	mkdir -p ../dist

create_completions:
	cd ../bin; _SIHM_COMPLETE=bash_source sihm > ./_sihm_complete_bash; _SIHM_COMPLETE=zsh_source sihm > ./_sihm_complete_zsh

$(SRC_JS_FILES) : $(SRC_TS_FILES)
	mkdir -p ../TEMPDIR
	cp $(SRC_DIR)/*.ts ../TEMPDIR
	(cd ../TEMPDIR; yarn init -p -y; yarn add three webpack webpack-cli dat.gui @types/three @types/dat.gui typescript; yarn tsc -t es6 *.ts);
	cp ../TEMPDIR/*.js $(TEMPLATE_SRC_DIR)
	rm -rf ../TEMPDIR

$(PYTHON_WHEEL_DIST): $(SRC_JS_FILES) $(PYTHON_PKG_FILES)
	cd ../; python setup.py bdist_wheel

install: $(PYTHON_WHEEL_DIST)
	pip uninstall -y sihm; pip install ../dist/*.whl

clean-python:
	rm -f ../dist/*.whl

$(DEB) : $(SRC_JS_FILES) ../dist
	sed -i 's/Version:.*/Version: $(VERSION)/g' ../packaging/debbuild/DEBIAN/control
	mkdir -p ../packaging/debbuild/$(DEB_PKG)
	cp -r ../packaging/debbuild/DEBIAN  ../packaging/debbuild/$(DEB_PKG)
	cp -r ../packaging/debbuild/usr ../packaging/debbuild/$(DEB_PKG)
	dpkg-deb --build --root-owner-group ../packaging/debbuild/$(DEB_PKG)
	cp ../packaging/debbuild/*.deb ../dist/

$(RPM) : $(SRC_JS_FILES) ../dist
	sed -i 's/Version:.*/Version: $(VERSION)/g' ../packaging/rpmbuild/SPECS/sihm.spec
	cd ../packaging/rpmbuild/SOURCES; mkdir -p sihm-$(VERSION); cd sihm-$(VERSION); cp ../../../../bin/_sihm* .; cd ..; tar -czvf sihm-$(VERSION).tar.gz sihm-$(VERSION); rm -rf sihm-$(VERSION)
	cd ../packaging/rpmbuild; rpmbuild --define "_topdir `pwd`" -ba SPECS/sihm.spec
	cp ../packaging/rpmbuild/RPMS/noarch/sihm-* ../dist/

$(BREW) : $(SRC_JS_FILES) ../dist
	sed -i 's/version .*/version "$(VERSION)"/g' ../packaging/sihm.rb
	cp ../packaging/sihm.rb ../dist/

deb: $(DEB)

rpm : $(RPM)

brew : $(BREW)

clean-deb:
	rm -rf ../packaging/debbuild/$(DEB_PKG)
	rm -rf ../packaging/debbuild/$(DEB_PKG).deb

clean-rpm: 
	rm -rf ../packaging/rpmbuild/BUILD 
	rm -rf ../packaging/rpmbuild/RPMS 
	rm -rf ../packaging/rpmbuild/SRPMS

dist: $(PYTHON_WHEEL_DIST) deb rpm brew

clean: clean-python clean-rpm clean-deb


