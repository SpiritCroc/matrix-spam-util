# matrix-spam-util for stress-testing/timing matrix client sync

Only do on dedicated test servers! 🙈

## Useful tips

To temporarily disable wlan on your phone while the script is running:

```
adb shell svc wifi disable ; ./spam.py -m 2 ; adb shell svc wifi enable
```
