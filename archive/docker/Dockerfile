# Use the latest Ubuntu LTS release as the base image
FROM ubuntu:20.04

# Set the timezone environment variable
ENV TZ=Europe/Berlin

# Create the /etc/timezone file with the timezone data and link /etc/localtime to the correct timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Update package lists and install essential packages
RUN apt-get update -y && \
    apt-get install -y \
        python3 \
        python3-pip \
        libglib2.0-dev \
        dbus \
        bluez \
        bluetooth \
        openssh-server && \
        mkdir /var/run/sshd \
        && apt-get clean

# Set the working directory in the container
WORKDIR /python_scripts

# COPY entrypoint.sh .

# Copy the rest of the application code to the container
COPY ./scripts/ /python_scripts/

# Install the API dependencies
RUN pip3 install -r requirements.txt

# Expose the port the container will run on
EXPOSE 22

CMD ["./entrypoint.sh"]

# Command to start the ssh
# CMD ["/usr/sbin/sshd", "-D"]