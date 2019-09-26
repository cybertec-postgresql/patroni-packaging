help:
	$(error Run make podman-image to create build image, then make debs to create debian packaged)

image:
	podman build -f fc30.Dockerfile . --tag patroni-packaging-fc30:latest

package:
	podman run --rm -v `pwd`:/patroni-packaging:Z -i -t patroni-packaging-fc30:latest

clean:
	rm -rf rpms

