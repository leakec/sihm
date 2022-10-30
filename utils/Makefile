install: 
	cd ..; python setup.py bdist_wheel; pip install dist/*.whl --force
create_completions:
	cd ../bin; _SIHM_COMPLETE=bash_source sihm > ./_sihm_complete_bash; _SIHM_COMPLETE=zsh_source sihm > ./_sihm_complete_zsh
