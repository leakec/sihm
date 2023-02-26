all: amoebic_glob.html

docs: amoebic_glob.html
	cp amoebic_glob.html ../../docs/examples

amoebic_glob.html : amoebic_glob.yaml
	sihm -i amoebic_glob.yaml params -j 3

clean:
	rm -f amoebic_glob.html
