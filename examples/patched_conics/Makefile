all: grav_assist.html

docs: grav_assist.html
	cp grav_assist.html ../../docs/examples

grav_assist.html : grav_assist.yaml
	sihm -i grav_assist.yaml params -j 3

grav_assist.yaml: grav_assist.yaml.in grav_assist.py
	python grav_assist.py

clean:
	rm -f grav_assist.yaml grav_assist.html
