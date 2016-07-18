#/bin/bash
set -eu
source shared.sh

export version

for version in $VERSIONS; do
    folder=python$version
    tag=envtpl-dev:$version

    mkdir -p $folder
    envtpl --keep-template -o $folder/Dockerfile Dockerfile.tpl
    docker build "$@" --tag $tag $folder
    docker run $tag
done
