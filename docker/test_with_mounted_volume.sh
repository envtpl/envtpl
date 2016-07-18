#/bin/bash
set -u
source shared.sh

for version in $VERSIONS; do
    tag=envtpl-dev:$version
    echo "Testing Python $version"
    docker run -it -v $PWD/..:/envtpl-dev/envtpl $tag
    echo
done
