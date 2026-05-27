#!/bin/sh

# cd base dir of project.
# the process is in the same shell as the starting shell.
cd $SPARROW_BASE_PATH

# login of $DOCKERHUB_DOMAIN.
# to be safety, never allow login with account in the command, you must login manually in your local system firstly.
# docker login -u $DOCKERHUB_USERNAME -p $DOCKERHUB_PASSWORD $DOCKERHUB_DOMAIN
# @Deprecated: it is not available, and not being called
# login() {
     # print_info "docker login {$DOCKERHUB_DOMAIN}..."
     # due to the reasons mentioned above, there is no need to do login explicitly here, as the session will be retained after manual login.
     # if ! docker login; then
     #    print_error "docker login failed"
     #    exit 1
     # fi
# }

# search image
search() {
    if ! [[ "${DOCKERHUB_REPO}" == *"docker.io"* ]]; then
        print_warn "Private cloud does not check whether the image exists"
        return 0
    fi

    print_info "start search image in dockerhub for public: $1... "

    search_image=$1

    # parse image reference: [registry/]repo/image[:tag]
    # remove docker.io prefix if present
    image_without_registry=$(echo "$search_image" | sed 's/^docker.io\///')

    # extract tag if exists
    if echo "$image_without_registry" | grep -q ":"; then
        tag=$(echo "$image_without_registry" | cut -d':' -f2)
        image_name=$(echo "$image_without_registry" | cut -d':' -f1)
        print_info "detected tag: $tag, image_name: $image_name"

        # for Docker Hub, if image name doesn't have a user, add library/ prefix
        if ! echo "$image_name" | grep -q "/"; then
            image_name="library/$image_name"
        fi

        # check tag via Docker Registry API
        print_info "checking tag existence via Docker Hub API... (if you seach tag, must use complete image name)"

        # get auth token
        token=$(curl -s "https://auth.docker.io/token?service=registry.docker.io&scope=repository:$image_name:pull" | sed -n 's/.*"token":"\([^"]*\)".*/\1/p')

        if [ -z "$token" ]; then
            print_warn "failed to get auth token, falling back to docker search without tag"
            # fall through to use docker search
        else
            # check manifest
            http_code=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $token" "https://registry-1.docker.io/v2/$image_name/manifests/$tag")

            if [ "$http_code" = "200" ]; then
                print_info "find it: $search_image (tag $tag exists)"
                return 0
            else
                print_warn "not find it: $search_image (tag $tag does not exist, HTTP code: $http_code)"
                return 1
            fi
        fi
    fi

    # no tag, use original docker search
    remove_prefix_search_image=$(echo "$search_image" | sed 's/^docker.io\///' | cut -d':' -f1)
    search_image_without_tag=$(echo "$search_image" | cut -d':' -f1)
    print_info "search search_image=${search_image}, search_image_without_tag=${search_image_without_tag}, remove_prefix_search_image=${remove_prefix_search_image}"

    # save and print the result of docker search
    search_result=$(docker search "$search_image_without_tag")
    print_info "docker search result:"
    echo "$search_result" | while IFS= read -r line; do echo "  $line"; done

    # print the grep result
    print_info "grep pattern: $remove_prefix_search_image"

    # check the match result (match anywhere in the line, not just start)
    matched_lines=$(echo "$search_result" | grep "$remove_prefix_search_image")
    if [ -n "$matched_lines" ]; then
        print_info "find it, matched lines:"
        echo "$matched_lines" | while IFS= read -r line; do echo "  $line"; done
        return 0  # find
    else
        print_warn "not find it"
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

    image="sparrow-$1-$2"
    version="$3"
    local_image="$image:$version"
    remote_image="$DOCKERHUB_REPO/$image:$version"
    print_info "pull image info: image=$image, version=$version, local_image=$local_image, remote_image=$remote_image"

    search_image="$DOCKERHUB_REPO/$image:$version"
    print_info "search image: $search_image..."
    if ! search "$search_image"; then
        print_warn "no image: $search_image"
        return 1
    fi

    print_info "pull image: $remote_image (platform: ${FROM_PLATFORM})..."
    if ! docker pull --platform "${FROM_PLATFORM}" "$remote_image"; then
        print_warn "pull failed: $remote_image"
        return 1
    fi

    # 搜索的时候只能搜索到镜像名称，无法搜索到平台信息，所以只能通过docker pull的方式来验证平台是否匹配。
    # When pulling with --platform, Docker may still pull an image if the manifest list includes a different architecture, but it will not match the requested platform. We need to verify the architecture after pulling to ensure we have the correct image.

    # Verify the pulled image actually matches the requested platform architecture.
    # docker pull --platform may succeed with a warning when the remote image only has a
    # different architecture (e.g. amd64 pulled when arm64 was requested).
    expected_arch=$(echo "${FROM_PLATFORM}" | cut -d'/' -f2)
    actual_arch=$(docker inspect --format '{{.Architecture}}' "$remote_image" 2>/dev/null)
    if [ "$actual_arch" != "$expected_arch" ]; then
        print_warn "platform mismatch: expected ${expected_arch}, got ${actual_arch} for ${remote_image}. Removing and falling back to build."
        docker image rm "$remote_image" 2>/dev/null
        return 1
    else
        print_info "platform match: expected ${expected_arch}, got ${actual_arch} for ${remote_image}."
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
        # push the timestamped version with service and version prefix for traceability.
        datestr=$(date +'%Y%m%d%H%M')
        upload_version="${service}.${version}_${type}.${datestr}"
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
