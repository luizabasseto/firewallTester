FROM python:3.10-slim

LABEL maintainer="Luiz Arthur <luizsantos@utfpr.edu.br>"

RUN apt update && apt install -y \
    iptables \
    tcpdump \
    lynx \
    iproute2 \
    net-tools \
    iputils-ping \
    nano \
    telnet \
    openssh-client \
    ftp \
    dnsutils \
    procps \
    traceroute \
    libgl1 \
    libxkbcommon-x11-0 \
    libxcb-xinerama0 \
    libxcb-cursor0 \
    libx11-xcb1 \
    && rm -rf /var/lib/apt/lists/*

COPY . /app
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY docker_infra/etc/firewall.sh /etc/
COPY docker_infra/etc/reset_firewall.sh /etc/

CMD ["tail", "-f", "/dev/null"]
