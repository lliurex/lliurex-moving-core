#!/bin/sh

if [ "$XDG_CURRENT_DESKTOP" != "" ]; then

	if [ "$UID" -gt "1041" ]; then  

		RC=0
		RET=$(n4d-client -h server -m is_frozen_user -c Golem -a $USER 2>/dev/null || echo False)

		# Fallback in case function is not supported. It should be, but still...
		RET=$( echo $RET | grep FUNCTION 1>/dev/null && echo False || echo $RET )

		# If not False (ie True), user is frozen
		echo $RET | grep False 1>/dev/null || RC=1

		eval $(n4d-vars getvalues SRV_LITE_MODE SRV_MOVING_MODE)
		
		OVERRIDE_FILE="/etc/classroom-servermode-override"
		if [ -e "$OVERRIDE_FILE" ]; then
			eval $(cat $OVERRIDE_FILE)
		fi
		
		RUN=0
		if [ $SRV_LITE_MODE = "True" ]; then
			if [ $SRV_MOVING_MODE = "False" ]; then
				RUN=1
			fi
		fi

		if [ $RUN -eq 0 ]; then
			llx-moving-cmd load || true

			if [ $RC -eq 1 ]; then
				dconf reset -f / || true
			fi
		fi
	fi
fi

