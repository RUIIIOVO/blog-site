---
title: "腾讯应用宝空包apk签名"
date: 2026-04-08T10:42:53+08:00
draft: false
---


腾讯应用宝要求上传空包时，本质上就是一件事：

> 用应用正式发布时使用的同一套签名证书，对平台提供的空包 APK 重新签名。

---

## 使用哪套签名

如果你平时在 Android Studio 里打正式包，就继续使用那套签名。

本次实际使用的是：

- `keystore`：`D:/Code/data_safe_android/app/keystore/laibudatavault.jks`
- `alias`：`datavault`

空包文件：

- `D:/Code/data_safe_android/yingyongbao_sign/tap_unsign.apk`

---

## 签名命令

```powershell
& "D:/App/SDK/build-tools/35.0.0/apksigner.bat" sign `
  --ks "D:/Code/data_safe_android/app/keystore/laibudatavault.jks" `
  --ks-key-alias "datavault" `
  --out "D:/Code/data_safe_android/yingyongbao_sign/tap_signed.apk" `
  "D:/Code/data_safe_android/yingyongbao_sign/tap_unsign.apk"
```

执行后输入：

- `keystore password`

---

## 验证签名

```powershell
& "D:/App/SDK/build-tools/35.0.0/apksigner.bat" verify -v "D:/Code/data_safe_android/yingyongbao_sign/tap_signed.apk"
```

如果输出里有以下结果，就说明签名完成：

```text
Verifies
Verified using v1 scheme (JAR signing): true
Verified using v2 scheme (APK Signature Scheme v2): true
Verified using v3 scheme (APK Signature Scheme v3): true
```

---
## 最终上传文件

签名后的文件：

- `D:/Code/data_safe_android/yingyongbao_sign/tap_signed.apk`

如果应用宝要求保留原始文件名，再按平台要求改名后上传。

---

# 使用 Android Studio 为应用签名

官方文档：
[https://developer.android.com/studio/publish/app-signing?hl=zh-cn#sign_release]()

