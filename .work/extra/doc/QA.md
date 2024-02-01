## Q&A

### 1、Install docker and docker-compose

#### Linux

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
