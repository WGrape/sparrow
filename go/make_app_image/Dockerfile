ARG FROM_PLATFORM
ARG IMAGE_BASIC_GO_VERSION
FROM --platform=${FROM_PLATFORM} sparrow-basic-go:${IMAGE_BASIC_GO_VERSION}

ENV GO111MODULE=on \
    GOPROXY=https://goproxy.cn,https://mirrors.aliyun.com/goproxy/,https://goproxy.io,direct \
    CGO_ENABLED=0 \
    GOOS=linux \
    GOARCH=amd64 \
    GOPATH=/go

# install go-zero
RUN go install github.com/zeromicro/go-zero/tools/goctl@latest \
    && goctl env check --install --verbose --force \
    && goctl env install --verbose --force \
    && goctl env check --verbose

# verify the go environment is deployed successfully, do not start the server.
WORKDIR /dist
COPY ./templates/go.mod /dist/go.mod
COPY ./templates/main.go /dist/main.go
RUN cd /dist/ && go mod download && go mod tidy && go build -o demoapp && rm -rf /dist
# CMD ["./demoapp"]
