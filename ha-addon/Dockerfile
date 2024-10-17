FROM python:3.9-slim

# Install necessary dependencies
RUN apt-get update && apt-get install -y git
RUN apt-get update && apt-get install -y git jq

# Clone the Botaffiumeiro repository
RUN git clone https://github.com/hectorzin/botaffiumeiro.git /botaffiumeiro

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
