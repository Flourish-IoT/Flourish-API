FROM ubuntu:20.04
SHELL [ "/bin/bash", "-c" ]

# install python 3.8 and pip
RUN apt update
RUN apt install -y python3.8 python3-distutils python3-pip python3-apt python3.8-venv

# create venv
WORKDIR /usr/bin/flourish
# "activates" venv
ENV VIRTUAL_ENV=/usr/bin/flourish/venv
RUN python3 -m venv ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

# install dependencies (will get cached)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# override this in prod
ENTRYPOINT ["./scripts/start.dev.sh" ]