# Use an official Python runtime as a parent image
FROM python:3.12-alpine

# Install necessary dependencies
RUN apk update && apk add --no-cache \
    git \
    jq \
    bash \
	curl

# Fetch the latest release tag from GitHub API and download the release archive
RUN latest_release=$(curl -s https://api.github.com/repos/hectorzin/botaffiumeiro/releases/latest | jq -r .tag_name) && \
    curl -L -o botaffiumeiro.tar.gz "https://github.com/hectorzin/botaffiumeiro/archive/${latest_release}.tar.gz" && \
    tar -xzvf botaffiumeiro.tar.gz && \
    mv "botaffiumeiro-${latest_release}" /botaffiumeiro && \
    rm botaffiumeiro.tar.gz

# Install project dependencies
WORKDIR /botaffiumeiro
RUN pip install -r requirements.txt

# Copy run.sh into the working directory
COPY run.sh /botaffiumeiro/
COPY json2yaml.py /botaffiumeiro/

# Ensure the script has execution permissions
RUN chmod +x /botaffiumeiro/run.sh

# Set the working directory to /botaffiumeiro
WORKDIR /botaffiumeiro

# Run the application using run.sh
CMD [ "bash", "/botaffiumeiro/run.sh" ]
