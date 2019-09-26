help:
	$(error Run make docker-image to create build image, then make debs to create debian packaged)

docker-image:
	docker build --tag=debian-build:9 .

package:
	docker run --rm -v `pwd`:/debian-build:Z debian-build:9 /debian-build/buildprocess.sh

clean:
	rm -rf *.build *.buildinfo *.changes *.tar.xz *.tar.gz *.deb *.dsc patroni-*/