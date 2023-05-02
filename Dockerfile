FROM debian:latest
LABEL maintainer = "millermoritz@gmail.com"

# build arguments
ARG TIMEZONE="Europe/Berlin"
ARG PROJECT_NAME

# update system
RUN apt-get update && apt-get upgrade -y

# set time zone to TIMEZONE
RUN rm -f /etc/localtime
RUN ln -s /usr/share/zoneinfo/${TIMEZONE} /etc/localtime

# install dependencies
RUN apt-get install -y \
    python3 \
    python3-pip

# discord
RUN pip3 install --upgrade discord.py

# GCP
RUN apt-get install -y \
    apt-transport-https \
    curl \
    ca-certificates \
    gnupg \
    openssh-client 

RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | tee /usr/share/keyrings/cloud.google.gpg && apt-get update -y && apt-get install google-cloud-sdk -y


# copy files
COPY ./appl /appl

# do config
RUN chmod +x /appl/run.py

# start container
WORKDIR /appl
CMD exec /appl/run.py