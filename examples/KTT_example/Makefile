all: ktt.html

docs: ktt.html
	cp ktt.html ../../docs/examples

ktt.html : ktt.yaml
	sihm -i ktt.yaml params -j 3

ktt.yaml: ktt.yaml.in ktt.py
	python ktt.py

clean:
	rm -f ktt.yaml ktt.html
