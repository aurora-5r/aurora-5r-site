#!/usr/bin/bash
#set -x
set -euo pipefail

WORKING_DIR="$(pwd)"
MY_DIR="$(cd "$(dirname "$0")" && pwd)"
pushd "${MY_DIR}" &>/dev/null || exit 1

DOC_FOLDER_PROD="docs_from_gdrive"

PREPROD_FOLDER=aurora5r

function log {
    echo -e "$(date +'%Y-%m-%d %H:%M:%S'):INFO: ${*} " >&2;
}

function usage {
cat << EOF
usage: ${0} <command> [<args>]

These are  ${0} commands used in various situations:

    build-site-prod            Build site and push it to prod
    build-site-preprod            Build site and push it to preprod
    preview-pages Starts the web server with preview of the website
    build-doc            Builds doc from gsuite
    build-pages-preprod            Builds pages for preprod
    build-pages-prod  Builds pages for prod
    check-site-links      Checks if the links are correct in the website
    help                  Display usage
    check-a11y             check a11y compliance

EOF
}

function run_command {
    log "Running command: $*"
    working_directory=$1
    shift
    pushd "${working_directory}"
    "$@"
    popd
}


function check_release {
  if [[ $1  =~ ^(production|preproduction)$ ]]; then
   return
  else
    echo "RELEASE not in  production|preproduction"
    exit 0
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

function build_pages {
    RELEASE=$1
    check_release ${RELEASE}
    log "Building pages for ${RELEASE}"
    copy_doc ${RELEASE}
    run_command "./site-content/" rm -rf dist


    if [[ "${RELEASE}" == "preproduction" ]]; then
        run_command "./site-content/" npm run dev
    else
        run_command "./site-content/" npm run build


    fi
    deploy_pages ${RELEASE}

}
function deploy_pages {
    log "Deploying  pages"
    RELEASE=$1
    check_release ${RELEASE}


    mkdir -p dist
    mkdir -p dist/${RELEASE}
    rm -rf dist/${RELEASE}/*


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

function copy_doc {
    RELEASE="$1"
    check_release ${RELEASE}

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
  RELEASE="$1"
  check_release ${RELEASE}

  log "Building full site for ${RELEASE}"
  build_doc
  build_pages ${RELEASE}

}


function build_doc {
    log "Building doc from gdrive"
    rm -rf "${DOC_FOLDER_PROD}/*"
    python -m gstomd --folder_id ${DOC_GDRIVE_PROD}  --dest "${DOC_FOLDER_PROD}" --config "conf/pydrive_settings.yaml"

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

if  [[ "${CMD}" == "help" ]]; then
    usage
    exit 0

    elif [[ "${CMD}" == "preview-pages" ]]; then
    copy_doc preproduction
    run_command "./site-content/" npm run preview
    elif [[ "${CMD}" == "build-pages-preprod" ]]; then
    build_pages preproduction
    elif [[ "${CMD}" == "build-pages-prod" ]]; then
    build_pages production
    elif [[ "${CMD}" == "build-site-preprod" ]]; then
    build_site  preproduction
    elif [[ "${CMD}" == "build-site-prod" ]]; then
    build_site production
    elif [[ "${CMD}" == "build-doc" ]]; then
    build_doc
    elif [[ "${CMD}" == "check-site-links" ]]; then
    run_command "./site-content/" ./check-links.sh
    elif [[ "${CMD}" == "check-a11y" ]]; then
    check_a11y
fi


