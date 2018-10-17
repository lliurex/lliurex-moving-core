#!/bin/bash

FIREFOX_DIR="$HOME/.mozilla/firefox/"
LOCK_FILE="lock"

if [ -d "$FIREFOX_DIR" ]; then

	find "$FIREFOX_DIR" -maxdepth 2 -name "$LOCK_FILE" -exec rm -rf {} \; || true

fi

