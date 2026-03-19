FROM    python:{{version}}

RUN     mkdir /envtpl-dev
WORKDIR /envtpl-dev
RUN     git clone https://github.com/andreasjansson/envtpl.git
WORKDIR /envtpl-dev/envtpl
RUN     pip install -e .
RUN     pip install -r tests/requirements.txt

CMD     ["pytest", "tests"]
