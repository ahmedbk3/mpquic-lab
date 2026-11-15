FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends mininet openvswitch-switch iperf3 iputils-ping iproute2 tcpdump net-tools python3 python3-pip procps nano ca-certificates git cmake build-essential pkg-config libssl-dev openssl && rm -rf /var/lib/apt/lists/*
RUN pip3 install --no-cache-dir os-ken==3.1.0
ARG PICOQUIC_REF=7044b9481146770c86a87b50984f1107ffc92272
RUN git clone https://github.com/private-octopus/picoquic.git /opt/picoquic && cd /opt/picoquic && git checkout ${PICOQUIC_REF} && cmake -DPICOQUIC_FETCH_PTLS=Y . && make -j$(nproc) picoquicdemo
RUN mkdir -p /opt/certs && openssl req -x509 -newkey rsa:2048 -nodes -days 365 -keyout /opt/certs/key.pem -out /opt/certs/cert.pem -subj /CN=test.example.com
COPY . /lab
WORKDIR /lab
RUN chmod +x /lab/entrypoint.sh
ENTRYPOINT ["/lab/entrypoint.sh"]
CMD ["bash"]
