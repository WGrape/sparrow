# Q&A DoC

## 1. Install and start docker/docker-compose

### (1) Install

#### a. Linux

```bash
# 1. install docker
curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun

# 2. install docker-compose by using curl.
# if it's very slow, you'd better use the next solution.
curl -L https://github.com/docker/compose/releases/download/1.3.1/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 3. install docker-compose by using yum.
yum install -y docker-compose
```

#### b. Mac

```Docker Desktop``` Installation of mac is here : https://docs.docker.com/desktop/release-notes/#4242 (you can choose any version).

### (2) Start

```bash
# Check Docker Status.
sudo systemctl status docker

# Start Docker.
sudo systemctl start docker
```

