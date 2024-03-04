#!/bin/sh

# cd base dir of project.
# the process is in the same shell as the starting shell.
cd $SPARROW_BASE_PATH

# login of $DOCKERHUB_DOMAIN.
# to be safety, never allow login with account in the command, you must login manually in your local system firstly.
# docker login -u $DOCKERHUB_USERNAME -p $DOCKERHUB_PASSWORD $DOCKERHUB_DOMAIN
login() {
    print_info "docker login {$DOCKERHUB_DOMAIN}..."
    # due to the reasons mentioned above, there is no need to do login explicitly here, as the session will be retained after manual login.
    # if ! docker login; then
    #    print_error "docker login failed"
    #    exit 1
    # fi
}

# search image
search() {
    search_image=$1
    remove_prefix_search_image=$(echo "$search_image" | sed 's/^docker.io\///')
    if docker search "$search_image" | grep -q "^$remove_prefix_search_image"; then
        return 0  # find
    else
        return 1  # not find
    fi
}

# pull images
pull() {
    # For security reasons, temporarily disable batch operations.
    if [ "$1" = "" ] || [ "$2" = "" ] || [ "$3" = "" ]; then
        print_error "pull() must pass 3 arguments: type(app/basic), service(go/nginx/etcd/...) and version(latest/...)"
        print_error "param1 = $1 | param2 = $2 | param3 = $3"
        print_error "If you passed the parameters correctly but failed during pull, it may be because you do not have this image."
        exit 1
    fi

    print_info "compute image..."
    image="sparrow-$1-$2"
    version="$3"
    local_image="$image:$version"
    remote_image="$DOCKERHUB_REPO/$image:$version"

    search_image="$DOCKERHUB_REPO/$image"
    print_info "search image: $search_image..."
    if ! search "$search_image"; then
        print_warn "no image: $search_image"
        return 1
    fi

    print_info "pull image: $remote_image..."
    if ! docker pull "$remote_image"; then
        print_warn "pull failed: $remote_image"
        return 1
    fi

    print_info "tag image: $remote_image => $local_image..."
    docker tag "$remote_image" "$local_image"
    docker image rm "$remote_image"
    return 0
}

# upload images.
upload() {
    while getopts "t:s:v:r:" opt; do
    case $opt in
        t)
        type="$OPTARG"
        ;;
        s)
        service="$OPTARG"
        service_upper=$(echo "$service" | awk '{print toupper($0)}')
        ;;
        v)
        version="$OPTARG"
        ;;
        r)
        replace="$OPTARG"
        ;;
        \?)
        echo "invalid option: -$OPTARG" >&2
        exit 1
        ;;
    esac
    done
    
    print_info "compute local_image and remote_image..."
    image="sparrow-${type}-${service}"
    if [ "${replace}" != "" ]; then
        upload_version="$version"
    else
        # push the timestamped version.
        datestr=$(date +'%Y%m%d%H%M')
        upload_version="1.0.${datestr}"
    fi
    remote_image="$DOCKERHUB_REPO/$image:$upload_version"
    local_image="$image:$version"

    print_info "tag image: $local_image => $remote_image"
    if ! docker tag "$local_image" "$remote_image"; then
        print_error "not find local_image: $local_image"
        exit 1
    fi

    print_info "upload image: $remote_image"
    docker push "$remote_image"
    docker image rm "$remote_image"
}
