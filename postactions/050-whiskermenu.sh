#!/bin/sh

LOCAL_FILE="$HOME/.config/xfce4/panel/whiskermenu-0.rc"

SKEL_PATH="/etc/skel/.config/xfce4/panel"
SKEL_FILE="$SKEL_PATH/whiskermenu-0.rc"

if [ ! -f $SKEL_FILE ]; then
	# NOTHING TO DO 
	exit 0
fi


# COPY SKEL FILE IF NOT FOUND IN HOME DIRECTORY

if [ ! -f  $LOCAL_FILE ]; then

	mkdir -p $SKEL_PATH || true
	cp $SKEL_FILE $LOCAL_FILE || true

fi

# COPY SKEL FILE IF LOCAL FILE DOESNT CONTAIN LLIUREX CONFIGURATIONS

RC=0
cat $LOCAL_FILE | grep lliurex 1>/dev/null || RC=1
if [ $RC = 1 ]; then

	cp $SKEL_FILE $LOCAL_FILE || true

fi

