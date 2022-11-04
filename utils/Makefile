# Get version from the version.py file
VERSION=$(shell cd ../src/sihm; python -c "from version import __version__; print(__version__)")
DEB_PKG=sihm_$(VERSION)-1_all

install: 
	cd ..; python setup.py bdist_wheel; pip install dist/*.whl --force

create_completions:
	cd ../bin; _SIHM_COMPLETE=bash_source sihm > ./_sihm_complete_bash; _SIHM_COMPLETE=zsh_source sihm > ./_sihm_complete_zsh

rpm-package :
	sed -i 's/Version:.*/Version: $(VERSION)/g' ../packaging/rpmbuild/SPECS/sihm.spec
	cd ../packaging/rpmbuild/SOURCES; mkdir -p sihm-$(VERSION); cd sihm-$(VERSION); cp ../../../../bin/_sihm* .; cd ..; tar -czvf sihm-$(VERSION).tar.gz sihm-$(VERSION); rm -rf sihm-$(VERSION)

deb-package:
	mkdir -p ../packaging/debbuild/$(DEB_PKG)
	cp -r ../packaging/debbuild/DEBIAN  ../packaging/debbuild/$(DEB_PKG)
	cp -r ../packaging/debbuild/usr ../packaging/debbuild/$(DEB_PKG)

deb: deb-package
	dpkg-deb --build --root-owner-group ../packaging/debbuild/$(DEB_PKG)

clean-deb:
	rm -rf ../packaging/debbuild/$(DEB_PKG)
	rm -rf ../packaging/debbuild/$(DEB_PKG).deb

rpm : rpm-package
	cd ../packaging/rpmbuild; rpmbuild --define "_topdir `pwd`" -ba SPECS/sihm.spec

clean-rpm: 
	rm -rf ../packaging/rpmbuild/BUILD 
	rm -rf ../packaging/rpmbuild/RPMS 
	rm -rf ../packaging/rpmbuild/SRPMS

template_project:
	mkdir -p ../TEMPDIR
	cp ../src/*.ts ../TEMPDIR
	(cd ../TEMPDIR; yarn init -p -y; yarn add three webpack webpack-cli dat.gui @types/three @types/dat.gui typescript; yarn tsc -t es6 *.ts);
	cp ../TEMPDIR/*.js ../src/sihm/template_project/src/
	rm -rf ../TEMPDIR

clean: clean-rpm clean-deb


