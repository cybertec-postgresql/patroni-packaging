help:
	$(error Run make docker-image to create build image, then make debs to create debian packaged)

docker-image:
	docker build . --tag patroni-packaging:latest

package:
	docker run --rm -v `pwd`:/patroni-packaging:Z -i -t patroni-packaging:latest

clean:
	rm -rf rpms