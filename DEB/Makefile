#!/bin/bash

help:
	$(error Run make dockerimage to create build image, then make debs to create debian packaged)

dockerimage:
	docker build --tag=debian-build:9 .

debs:
	docker run --rm -v `pwd`:/debian-build debian-build:9 /debian-build/buildprocess.sh
