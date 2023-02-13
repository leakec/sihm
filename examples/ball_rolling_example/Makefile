all: ball_rolling.html

docs: ball_rolling.html
	cp ball_rolling.html ../../docs/examples

ball_rolling.html : ball_rolling.yaml
	sihm -i ball_rolling.yaml params -j 3

ball_rolling.yaml: ball_rolling.yaml.in ball_rolling.py
	python ball_rolling.py

clean:
	rm -f ball_rolling.yaml ball_rolling.html
