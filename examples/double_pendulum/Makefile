all: double_pendulum.html

docs: double_pendulum.html
	cp double_pendulum.html ../../docs

double_pendulum.html : double_pendulum.yaml
	sihm -i double_pendulum.yaml params -j 3

double_pendulum.yaml: double_pendulum.yaml.in double_pendulum.py
	python double_pendulum.py

clean:
	rm -f double_pendulum.yaml double_pendulum.html
