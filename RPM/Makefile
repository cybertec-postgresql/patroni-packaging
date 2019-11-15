help:
	$(error Run make docker-image to create build image, then make debs to create debian packaged)

podman-image:
	podman build . --tag patroni-packaging:latest

podman-package:
	podman run --rm -v `pwd`:/patroni-packaging:Z -i -t patroni-packaging:latest

docker-image:
	docker build . --tag patroni-packaging:latest

docker-package:
	docker run --rm -v `pwd`:/patroni-packaging:Z -i -t patroni-packaging:latest

clean:
	rm -rf rpms