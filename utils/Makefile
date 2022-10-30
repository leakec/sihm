install: 
	cd ..; python setup.py bdist_wheel; pip install dist/*.whl --force
create_completions:
	cd ../bin; _SIHM_COMPLETE=bash_source sihm > ./_sihm_complete_bash; _SIHM_COMPLETE=zsh_source sihm > ./_sihm_complete_zsh

rpm :
	cd ../packaging/rpmbuild/SOURCES; cp ../../../bin/_sihm* .; tar -czvf _sihm_complete_zsh.tar.gz _sihm_complete_zsh; tar -czvf _sihm_complete_bash.tar.gz _sihm_complete_bash; rm _sihm_complete_zsh _sihm_complete_bash
