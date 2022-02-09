FROM python:3.10.2-bullseye
SHELL [ "/bin/bash", "-c" ]

# create venv
WORKDIR /usr/bin/flourish
# "activates" venv
ENV VIRTUAL_ENV=/usr/bin/flourish/venv
RUN python3 -m venv ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

# update pip
RUN pip install --upgrade pip setuptools wheel

# install dependencies (will get cached)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# override this in prod
ENTRYPOINT ["./scripts/start.dev.sh" ]