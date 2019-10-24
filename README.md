# About AnnoSig

This App was developed as a interface to asses the quality of fetal ECGs.
Therefore a stack of signals is presented to the user.
Users can assign a continues score from 0 to 1 to the presentet signal.
It is based on pictures so its highly adjustable.

The App was part of a Crowdsourcing approach of fetal ECG Signal Quality - therfore a simple server is needed to handel the requests.


## Installation

You should use a virtualenv for python, then:
```sh
cd example
pip install -r requirements.txt
```

### Run on Android

#### Install dependencies (Ubuntu)

There are actually two lists of dependencies: [`buildozer` docs](https://buildozer.readthedocs.io/en/latest/installation.html#targeting-android) and [`buildozer` Dockerfile](https://github.com/kivy/buildozer/blob/master/Dockerfile#L45-L65)
If you want to be sure, install both.

I just installed:
```sh
apt install openjdk-8-jdk
apt install libffi-dev      # dependency compile _ctypes
apt install adb             # manage android devices
# apt install ccache        # don't know if this is required
```
You probably need some build tools too (`automake etc.`).

**Note:** If you have multiple versions of Java installed, you might get this error:

```
# Android NDK installation done.
# Installing/updating SDK platform tools if necessary
# Run '/home/jonas/.buildozer/android/platform/android-sdk/tools/bin/sdkmanager tools platform-tools'
# Cwd /home/jonas/.buildozer/android/platform/android-sdk
Exception in thread "main" java.lang.NoClassDefFoundError: javax/xml/bind/annotation/XmlSchema
	at com.android.repository.api.SchemaModule$SchemaModuleVersion.<init>(SchemaModule.java:156)
	at com.android.repository.api.SchemaModule.<init>(SchemaModule.java:75)
	at com.android.sdklib.repository.AndroidSdkHandler.<clinit>(AndroidSdkHandler.java:81)
	at com.android.sdklib.tool.sdkmanager.SdkManagerCli.main(SdkManagerCli.java:73)
	at com.android.sdklib.tool.sdkmanager.SdkManagerCli.main(SdkManagerCli.java:48)
Caused by: java.lang.ClassNotFoundException: javax.xml.bind.annotation.XmlSchema
	at java.base/jdk.internal.loader.BuiltinClassLoader.loadClass(BuiltinClassLoader.java:583)
	at java.base/jdk.internal.loader.ClassLoaders$AppClassLoader.loadClass(ClassLoaders.java:178)
	at java.base/java.lang.ClassLoader.loadClass(ClassLoader.java:521)
	... 5 more
# Command failed: /home/jonas/.buildozer/android/platform/android-sdk/tools/bin/sdkmanager tools platform-tools
# 
# Buildozer failed to execute the last command
# The error might be hidden in the log above this error
# Please read the full log, and search for it before
# raising an issue with buildozer itself.
# In case of a bug report, please add a full log with log_level = 2
```

You have to configure JDK 8 as the default:
```sh
sudo update-alternatives --config javac
sudo update-alternatives --config java
```


#### Install dependencies (Windows)

**TODO**

```sh
apt install xclip
```

#### Deploy

Before you can deploy to Android, you have to 
1. Enable USB-Debugging on your phone. The setting is located in the developer menu which can be enabled by tapping repeatedly on the kernel version in your phone settings software information.
2. Authorize the computer. You will get a dialog on your phone on the first deploy.

Then run:
```sh
cd example
buildozer android debug   # build the debug target
buildozer android deploy  # push app to phone
buildozer android run     # start
```

The steps can also be combiled:
```sh
buildozer android debug deploy run
```

To show logs, i.e. `print()` statements:
```sh
buildozer android logcat
```

The build `.apk` can now also be found in `bin/`.


### Run on Desktop

```sh
cd example
python main.py
```