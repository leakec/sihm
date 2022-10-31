install: 
	cd ..; python setup.py bdist_wheel; pip install dist/*.whl --force

create_completions:
	cd ../bin; _SIHM_COMPLETE=bash_source sihm > ./_sihm_complete_bash; _SIHM_COMPLETE=zsh_source sihm > ./_sihm_complete_zsh

rpm-package :
	cd ../packaging/rpmbuild/SOURCES; mkdir -p sihm-0.0.1; cd sihm-0.0.1; cp ../../../../bin/_sihm* .; cd ..; tar -czvf sihm-0.0.1.tar.gz sihm-0.0.1; rm -rf sihm-0.0.1

rpm : rpm-package
	cd ../packaging/rpmbuild; rpmbuild --define "_topdir `pwd`" -ba SPECS/sihm.spec

template_project:
	mkdir -p ../TEMPDIR
	cp ../src/*.ts ../TEMPDIR
	(cd ../TEMPDIR; yarn init -p -y; yarn add three webpack webpack-cli dat.gui @types/three @types/dat.gui typescript; yarn tsc -t es6 *.ts);
	cp ../TEMPDIR/*.js ../src/sihm/template_project/src/
	rm -rf ../TEMPDIR

