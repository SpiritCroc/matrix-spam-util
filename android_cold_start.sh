#!/bin/bash

set -e

package="$1"
if [ -z "$package" ]; then
    echo "Usage: $0 package/activity [spam.py args...]"
    exit 1
fi

shift

if [[ "$package" =~ "/" ]]; then
    activity="$(echo "$package" | sed 's|.*/||')"
    package="$(echo "$package" | sed 's|/.*||')"
else
    activity=
fi

echo "Disable wifi..."
adb shell svc wifi disable

echo "Kill $package..."
adb shell am force-stop "$package"

echo "Spam..."
./spam.py "$@"

echo "Enable wifi..."
adb shell svc wifi enable

echo "Launch $package..."
if [ -z "$activity" ]; then
    # Guess activity from launcher intent
    adb shell monkey -p "$package" -c android.intent.category.LAUNCHER 1
else
    # TODO fix me?
    adb shell am start -n "$package"/"$activity"
fi

while [ -z "$pid" ]; do
    sleep 1
    echo "Looking for PID..."
    pid=`adb shell ps -o name,pid|grep com.beeper.chat.debug|sed 's|.*\s\s*||'`
done

echo "PID of $package: $pid, filtered logcat..."
adb logcat --pid "$pid" | grep --color "secs parsing"
