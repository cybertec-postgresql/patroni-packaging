FROM debian:9

RUN apt-get update && apt-get install -y \
	build-essential fakeroot devscripts \
	python-psycopg2 python-setuptools python-dev libyaml-dev \
	python3-virtualenv dh-virtualenv python3-psycopg2 \
  && rm -rf /var/lib/apt/lists/*

CMD ["bash"]
