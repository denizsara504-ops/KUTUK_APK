[app]
title         = Kutuk Sorgulama
package.name  = kutuксorgulama
package.domain= org.kutuk

# Kaynak
source.dir    = src
source.include_exts = py,kv,png,jpg,sqlite

# Versiyon
version       = 1.0

# Requirements - sadece gerekli olanlar
requirements  = python3,kivy==2.3.0,sqlite3

# Orientasyon - tablet için her iki yön
orientation   = landscape

# Android ayarları
android.minapi        = 21
android.ndk           = 25b
android.sdk           = 33
android.accept_sdk_license = True

# İzinler
android.permissions = \
    INTERNET,\
    READ_EXTERNAL_STORAGE,\
    WRITE_EXTERNAL_STORAGE,\
    MANAGE_EXTERNAL_STORAGE

# Mimari - modern tabletler için
android.archs = arm64-v8a, armeabi-v7a

# APK imzalama (debug mod)
android.debug = True

# Tam ekran
fullscreen    = 0

# Log seviyesi
log_level     = 2

[buildozer]
log_level = 2
warn_on_root = 1
