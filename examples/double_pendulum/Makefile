all: double_pendulum.html

docs: double_pendulum.html
	cp double_pendulum.html ../../docs/examples

double_pendulum.html : double_pendulum.yaml
	sihm -i double_pendulum.yaml params -j 3

double_pendulum.yaml: double_pendulum.yaml.in double_pendulum.py double_pendulum.urdf pendulum.obj
	python double_pendulum.py

pendulum.obj: pendulum.FCStd
	python create_files.py --export-obj

double_pendulum.urdf: pendulum.FCStd double_pendulum.urdf.in
	python create_files.py --export-urdf

clean:
	rm -f double_pendulum.yaml double_pendulum.html pendulum.obj pendulum.mtl double_pendulum.urdf pendulum_normal_map.png
