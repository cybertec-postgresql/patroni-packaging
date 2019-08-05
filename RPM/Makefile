default:

docker-image:
	docker build . --tag patroni-packaging:latest

rpm:
	docker run --rm -v `pwd`:/patroni-packaging:Z -i -t patroni-packaging:latest