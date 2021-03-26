#!/usr/bin/bash
#set -x
set -euo pipefail

WORKING_DIR="$(pwd)"
MY_DIR="$(cd "$(dirname "$0")" && pwd)"
pushd "${MY_DIR}" &>/dev/null || exit 1

SRS_CALCULATOR="../srs-calculator/dist"

DOC_FOLDER_PROD="docs_from_gdrive"

IMAGE_NAME=aurora-5r-site
CONTAINER_NAME=aurora-5r-site-c
PREPROD_FOLDER=aurora5r

function log {
    echo -e "$(date +'%Y-%m-%d %H:%M:%S'):INFO: ${*} " >&2;
}

function usage {
cat << EOF
usage: ${0} <command> [<args>]

These are  ${0} commands used in various situations:

    build-site            Build site and push it to prod and preprod
    preview-pages Starts the web server with preview of the website
    build-doc            Builds doc from gsuite
    copy-doc            copy last version of doc to site folder
    build-pages            Builds pages
    shell                 Start shell
    build-image           Build a Docker image with a environment
    install-node-deps     Download all the Node dependencies
    check-site-links      Checks if the links are correct in the website
    lint-css              Lint CSS files
    lint-js               Lint Javascript files
    cleanup               Delete the virtual environment in Docker
    stop                  Stop the environment
    help                  Display usage
    check-a11y             check a11y compliance

Unrecognized commands are run as programs in the container.

For example, if you want to display a list of files, you
can execute the following command:

    $0 ls

The following command can also be performed from the Docker environment:
install-node-deps, preview, build-site, lint-css, lint-js.

The lint-css and lint-js accept paths in arguments. If no path is given, the script
will be executed for all supported files

EOF
}

function ensure_image_exists {
    log "Checking if image exists: ${IMAGE_NAME}"
    if [[ ! $(docker images "${IMAGE_NAME}" -q) ]]; then
        log "Image not exists."
        build_image
    fi
}

function ensure_container_exists {
    log "Checking if container exists: ${CONTAINER_NAME}"
    if [[ ! $(docker container ls -a --filter="Name=${CONTAINER_NAME}" -q ) ]]; then
        log "Container not exists"
        docker run \
        --detach \
        --name "${CONTAINER_NAME}" \
        --volume "$(pwd):/opt/site/" \
        --publish 8081:8081 \
        --publish 3001:3001 \
        "${IMAGE_NAME}" sh -c 'trap "exit 0" INT; while true; do sleep 30; done;'
        return 0
    fi
}

function ensure_container_running {
    log "Checking if container running: ${CONTAINER_NAME}"
    container_status="$(docker inspect "${CONTAINER_NAME}" --format '{{.State.Status}}')"
    log "Current container status: ${container_status}"
    if [[ ! "${container_status}" == "running" ]]; then
        log "Container not running. Starting the container."
        docker start "${CONTAINER_NAME}"
    fi
}

function ensure_node_module_exists {
    log "Checking if node module exists"
    if [[ ! -d site-content/node_modules/ ]] ; then
        log "Missing node dependencies. Start installation."
        run_command "/opt/site/site-content/" npm install
        log "Dependencies installed."
    fi
}

function ensure_that_website_is_build {
    log "Check if site-content/dist/index.html file exists"
    if [[ ! -f site-content/dist/index.html ]] ; then
        log "The website is not built."
        exit 1

    fi
}

function build_image {
    log "Start building image"
    docker build -t aurora-5r-site .
    log "End building image"
}

function run_command {
    log "Running command: $*"
    working_directory=$1
    shift
    if [[ -f /.dockerenv ]] ; then

        pushd "${working_directory}"
        exec "$@"
    else
        if ! test -t 0; then
            docker exec \
            --interactive \
            --workdir "${working_directory}" \
            "${CONTAINER_NAME}" "$@"
        else

            docker exec \
            --tty \
            --interactive \
            --workdir "${working_directory}" \
            "${CONTAINER_NAME}" "$@"
        fi
    fi
}

function prepare_environment {
    log "Preparing environment"
    if [[ ! -f /.dockerenv ]] ; then
        ensure_image_exists
        ensure_container_exists
        ensure_container_running
    fi
}

function prevent_docker {
    if [[ -f /.dockerenv ]] ; then
        echo "This command is not supported in the Docker environment. Run this command from the host system."
        exit 1
    fi
}

function relativepath {
    source=$1
    target=$2

    common_part=$source # for now
    result="" # for now

    while [[ "${target#$common_part}" == "${target}" ]]; do
        # no match, means that candidate common part is not correct
        # go up one level (reduce common part)
        common_part="$(dirname "$common_part")"
        # and record that we went back, with correct / handling
        if [[ -z $result ]]; then
            result=".."
        else
            result="../$result"
        fi
    done

    if [[ $common_part == "/" ]]; then
        # special case for root (no common path)
        result="$result/"
    fi

    # since we now have identified the common part,
    # compute the non-common part
    forward_part="${target#$common_part}"

    # and now stick all parts together
    if [[ -n $result ]] && [[ -n $forward_part ]]; then
        result="$result$forward_part"
        elif [[ -n $forward_part ]]; then
        # extra slash removal
        result="${forward_part:1}"
    fi
    echo "$result"
}

function run_lint {
    script_working_directory=$1
    command=$2
    shift 2

    DOCKER_PATHS=()
    for E in "${@}"; do
        ABS_PATH=$(cd "${WORKING_DIR}" && realpath "${E}")
        DOCKER_PATHS+=("/opt/site/$(relativepath "$(pwd)" "${ABS_PATH}")")
    done
    run_command "${script_working_directory}" "${command}" "${DOCKER_PATHS[@]}"
}


function build_pages {
    RELEASE=$1
    log "Building pages for ${RELEASE}"
    copy_doc ${RELEASE}
    run_command "/opt/site/site-content/" rm -rf dist
    if [[ "${RELEASE}" == "preproduction" ]]; then
        run_command "/opt/site/site-content/" npm run dev
    else
        run_command "/opt/site/site-content/" npm run build


    fi
    deploy_pages ${RELEASE}

}
function deploy_pages {
    log "Deploying landing pages"
    RELEASE=$1

    mkdir -p dist
    mkdir -p dist/${RELEASE}
    rm -rf dist/${RELEASE}/*

    echo ${SRS_CALCULATOR}
    if [[ -n "${SRS_CALCULATOR}" ]]; then
        log "Getting SRS_CALCULATOR from ${SRS_CALCULATOR}"
        mkdir -p dist/${RELEASE}/srs-calculator
        verbose_copy ${SRS_CALCULATOR}/. dist/${RELEASE}/srs-calculator/
    else
        log "no SRS_CALCULATOR  ${SRS_CALCULATOR}"
    fi
    verbose_copy site-content/dist/. dist/${RELEASE}/
    if [[ "${RELEASE}" == "preproduction" ]]; then
        if [[ -z "${URL_PREPROD+x}" ]]; then
            echo "URL_PREPROD environment variable not set"
            exit 0
        else
            log "Copy dist in /var/www/html/${PREPROD_FOLDER} for preprod tests"
            sudo mkdir -p /var/www/html/${PREPROD_FOLDER}
            sudo rm -rf /var/www/html/${PREPROD_FOLDER}/*;sudo cp -rp dist/${RELEASE}/* /var/www/html/${PREPROD_FOLDER}

            sudo sed -i "s/https:\/\/${URL_PROD}/http:\/\/${URL_PREPROD}\//g" /var/www/html/${PREPROD_FOLDER}/sitemap.xml
            sudo sed -i "s/https:\/\/${URL_PROD}/http:\/\/${URL_PREPROD}\//g" /var/www/html/${PREPROD_FOLDER}/robots.txt

            for page in $(find /var/www/html/${PREPROD_FOLDER} -name "*.html"); do
                sudo sed -i "s/https:\/\/${URL_PROD}/http:\/\/${URL_PREPROD}\//g" ${page}

            done

        fi
        elif [[ "${RELEASE}" == "production" ]]; then
        if [[ -z "${SSH_PROD+x}" ]]; then
            echo "SSH_PROD environment variable not set"
            exit 0
        else
            rsync -rh --progress --delete dist/${RELEASE}/* ${SSH_PROD}
            exit 0
        fi
    fi
}


function verbose_copy {
    source="$1"
    target="$2"
    log "Copying '$source' to '$target'"
    mkdir -p "${target}"
    cp -R "$source" "$target"
}

function assert_file_exists {
    file_path="$1"
    if [[ ! -f "${file_path}" ]]; then
        echo "Missing file: ${file_path}":
        exit 1
    fi
}


function copy_doc {
    RELEASE="$1"
    log "copy_doc for ${RELEASE}"


    for collection in ${DOC_FOLDER_PROD}/production/* ; do
        # Process directories only,
        if [ ! -d "${collection}" ]; then
            continue;
        fi
        collection_name="$(basename -- "${collection}")"
        mkdir -p "site-content/src/${collection_name}/"
        find  "site-content/src/${collection_name}/"  -maxdepth 1 -mindepth 1 -type d -exec  rm -rf {} +

        verbose_copy "${collection}/." "site-content/src/${collection_name}"

    done
    if [[ "${RELEASE}" == "production" ]]; then
        log "remove drafts"
        find  "site-content/src/"  -type d -name 'drafts' -exec  rm -rf {} +
    fi
}
function build_site {
    log "Building full site"

    build_doc
    log "... for preproduction"

    copy_doc preproduction
    build_pages preproduction

    log "... for production"

    copy_doc production
    build_pages production


}


function build_doc {
    log "Building doc from gdrive"
    rm -rf "${DOC_FOLDER_PROD}/*"

    python -m gstomd --folder_id ${DOC_GDRIVE_PROD}  --dest "${DOC_FOLDER_PROD}" --config "conf/pydrive_settings.yaml"

}



function cleanup_environment {
    container_status="$(docker inspect "${CONTAINER_NAME}" --format '{{.State.Status}}')"
    log "Current container status: ${container_status}"
    if [[ "${container_status}" == "running" ]]; then
        log "Container running. Killing the container."
        docker kill "${CONTAINER_NAME}"
    fi

    if [[ $(docker container ls -a --filter="Name=${CONTAINER_NAME}" -q ) ]]; then
        log "Container exists. Removing the container."
        docker rm "${CONTAINER_NAME}"
    fi

    if [[ $(docker images "${IMAGE_NAME}" -q) ]]; then
        log "Images exists. Deleting the image."
        docker rmi "${IMAGE_NAME}"
    fi
}



function check_a11y {
    log "Checking a11y compliance... "
    if [[ -z "${URL_PREPROD+x}" ]]; then
        echo "you must set URL_PREPROD environment variable"
        exit 1
    fi

    pa11y-ci --sitemap "http://$URL_PREPROD"/sitemap.xml

}


# - - - - - MAIN
if [[ ! -f conf/conf-secret.sh ]] ; then
    log "Missing configuration file conf/conf-secret.sh"
    exit 1
fi

. ./conf/conf-secret.sh

if [[ "$#" -eq 0 ]]; then
    echo "You must provide at least one command."
    echo
    usage
    exit 1
fi

CMD=$1

shift

# Check fundamentals commands
if [[ "${CMD}" == "build-image" ]] ; then
    prevent_docker
    build_image
    exit 0
    elif [[ "${CMD}" == "stop" ]] ; then
    prevent_docker
    docker kill "${CONTAINER_NAME}"
    exit 0
    elif [[ "${CMD}" == "cleanup" ]] ; then
    prevent_docker
    cleanup_environment
    exit 0
    elif [[ "${CMD}" == "help" ]]; then
    usage
    exit 0
fi

prepare_environment

# Check container commands
if [[ "${CMD}" == "install-node-deps" ]] ; then
    run_command "/opt/site/site-content/" npm install
    elif [[ "${CMD}" == "preview-pages" ]]; then
    ensure_node_module_exists
    run_command "/opt/site/site-content/" npm run preview
    elif [[ "${CMD}" == "build-pages-preprod" ]]; then
    ensure_node_module_exists
    build_pages preproduction
    elif [[ "${CMD}" == "build-pages-prod" ]]; then
    ensure_node_module_exists
    build_pages production
    elif [[ "${CMD}" == "build-site" ]]; then
    ensure_node_module_exists
    build_site

    elif [[ "${CMD}" == "build-doc" ]]; then
    build_doc

    elif [[ "${CMD}" == "check-site-links" ]]; then
    ensure_node_module_exists
    ensure_that_website_is_build
    run_command "/opt/site/site-content/" ./check-links.sh

    elif [[ "${CMD}" == "check-a11y" ]]; then
    ensure_that_website_is_build
    check_a11y
    elif [[ "${CMD}" == "lint-js" ]]; then
    ensure_node_module_exists
    if [[ "$#" -eq 0 ]]; then
        run_command "/opt/site/site-content/" npm run lint:js
    else
        run_lint "/opt/site/site-content/" ./node_modules/.bin/eslint "$@"
    fi
    elif [[ "${CMD}" == "lint-css" ]]; then
    ensure_node_module_exists
    if [[ "$#" -eq 0 ]]; then
        run_command "/opt/site/site-content/" npm run lint:css
    else
        run_lint "/opt/site/site-content/" ./node_modules/.bin/stylelint "$@"
    fi
    elif [[ "${CMD}" == "shell" ]]; then
    prevent_docker
    docker exec -ti "${CONTAINER_NAME}" /bin/bash
else
    prevent_docker
    docker exec -ti "${CONTAINER_NAME}" "${CMD}" "$@"
fi

popd &>/dev/null || exit 1
