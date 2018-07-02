FROM debian:9

RUN apt-get update && apt-get install -y \
	build-essential fakeroot devscripts \
	python3-psycopg2 python3-setuptools python3-dev libyaml-dev \
	python3-virtualenv dh-virtualenv \
        wget git ruby ruby-dev rubygems build-essential \
        curl \
  && rm -rf /var/lib/apt/lists/* \
  && gem install --no-ri --no-rdoc fpm \
  && cd /opt \
  && wget https://dl.google.com/go/go1.10.3.linux-amd64.tar.gz \
  && tar -xzf go1.10.3.linux-amd64.tar.gz

CMD ["bash"]
