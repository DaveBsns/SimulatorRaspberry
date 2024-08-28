#!/bin/bash

# start services
service dbus start
service bluetooth start

# Start sshd service
# /usr/sbin/sshd -D