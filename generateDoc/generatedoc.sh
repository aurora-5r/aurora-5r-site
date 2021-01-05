#!/usr/bin/env bash

set -euo pipefail

WORKING_DIR="$(pwd)"
MY_DIR="$(cd "$(dirname "$0")" && pwd)"
pushd "${MY_DIR}" &>/dev/null || exit 1


function log {
    echo -e "$(date +'%Y-%m-%d %H:%M:%S'):INFO: ${*} " >&2;
}

function usage {
cat << EOF
usage: ${0} <command> [<args>]

These are  ${0} commands used in various situations:

    build
    help                  Display usage



EOF
}


function build_doc {
    
    

}


if [[ "$#" -eq 0 ]]; then
    echo "You must provide at least one command."
    echo
    usage
    exit 1
fi

CMD=$1

shift

if [[ "${CMD}" == "build" ]] ; then
    
    build_doc $*
    exit 0
    elif [[ "${CMD}" == "help" ]]; then
    usage
    exit 0
fi
usage
exit 1