#!/bin/sh

LOCK_FILE="$HOME/.config/libreoffice/4/.lock"

if [ -f  $LOCK_FILE ]; then

	rm -rf $LOCK_FILE || true

fi


