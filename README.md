# iOS-U2F-Bridge
Relay U2F packet between desktop and iOS device.

**WARNING:**

This project is still in its pre-alpha stage.  Serious refactoring and
documentations are needed.

Currently v2f.py only supports Linux and Python 3.5+.  The code was tested
using Google Chrome inside a 64-bit Ubuntu 16.04 desktop environment.



# v2f.py is a virtual U2F device

Clone this source code repository

```bash
git clone https://github.com/concise/v2f.py
cd v2f.py
```


Tweak permissions of some files before running v2f, which needs uhid and
hidraw.  An easy way to do that is just making `/dev/uhid` and `/dev/hidraw*`
device nodes universally read-writable

```bash
sudo bash hack-linux-for-v2f
```


Run v2f (default: store everything under ~/.v2f directory)

```bash
python3 v2f.py
```


Run v2f with a specified device information directory

```bash
python3 v2f.py ~/.my-v2f-info-dir
```
