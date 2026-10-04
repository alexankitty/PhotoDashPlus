#!/usr/bin/env bash
read -s -p "Keystore password: " RELEASE_STORE_PASSWORD && echo && \
RELEASE_STORE_FILE=/home/alexandra/keys/photodashplus.jks RELEASE_STORE_PASSWORD="$RELEASE_STORE_PASSWORD" \
./gradlew :photodashplus:assembleRelease; unset RELEASE_STORE_PASSWORD

