docker run -it --rm --name mqtt-broker -p 1883:1883 -v "$PWD/mosquitto/config:/mosquitto/config:ro" eclipse-mosquitto:latest
