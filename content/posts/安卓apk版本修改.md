---
title: "安卓apk版本修改"
date: 2026-04-08T10:42:54+08:00
draft: false
---

config.gradle  versionName

```
ext {  
    // 应用兼容最低SDK版本  
    minSdk = 21  
    targetSdk = 30  
    buildToolsVersion = '35.0.0'  
    compileSdkVersion = 35  
//    compileSdkVersion = 32  
    versionCode = 115  
    versionName = '1.1'  
  
  
    frescoVersion = '2.6.0'  
    materialVersion = '1.4.0'  
  
  
    liboSrcRoot         = '/Users/js/libreoffice_android'  
    liboWorkdir         = '/Users/js/libreoffice_android/workdir'  
    liboInstdir         = '/Users/js/libreoffice_android/instdir'  
    liboEtcFolder       = 'program'  
    liboUreMiscFolder   = 'program'  
    liboSharedResFolder = 'program/resource'  
    liboUREJavaFolder   = 'program/classes'  
    liboShareJavaFolder = 'program/classes'  
    liboExampleDocument = '/Users/js/libreoffice_android/android/default-document/example.odt'  
    liboVersionMajor    = '5'  
    liboVersionMinor    = '3'  
    liboGitFullCommit   = '228a4ff4fe70ca5b7306b2c8312b9a1d3f618118'  
    liboNdkGdbserver    = '/Users/js/Library/Android/sdk/ndk/21.4.7075529/prebuilt/android-arm/gdbserver/gdbserver'  
    liboAndroidAppAbi   = 'armeabi-v7a'  
  
  
    // Dependencies Libraries  
    dependencies = ["fresco"        : "com.facebook.fresco:fresco:" + frescoVersion,  
                    "fresco-gif"    : "com.facebook.fresco:animated-gif:" + frescoVersion,  
                    "fresco-okhttp3": "com.facebook.fresco:imagepipeline-okhttp3:" + frescoVersion,  
                    "fresco-webpsupport"        : "com.facebook.fresco:webpsupport:" + frescoVersion,  
                    "material": "com.google.android.material:material:" + materialVersion  
  
    ]  
  
}
```
