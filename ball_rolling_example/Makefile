all: ball_rolling.yaml
	sihm -i ball_rolling.yaml params -j 3
ball_rolling.yaml: ball_rolling.yaml.in ball_rolling.py
	python ball_rolling.py

clean:
	rm -f ball_rolling.yaml ball_rolling.html
