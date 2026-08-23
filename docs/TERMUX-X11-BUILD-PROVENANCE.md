# Termux:X11 superfix build provenance

> **Documento histórico pre-migración.** Describe la identidad shared-UID que
> se investigó antes de instalar la edición standalone. El estado vigente es
> Termux:X11 `1.03.01-f68cd36-21.08.26`, UID 10423, aislado de Termux UID 10602.
> Véase `docs/MACDESK-V6-BUG-RESOLUTION-CERTIFICATE.md`.

## Installed identity

- `INSTALLED_VERSION=1.03.01-50ac80f-19.08.26`
- `INSTALLED_REVISION=50ac80fb2d4a475e323e752d17fcc0483c3c99fc`
- `SOURCE_REPOSITORY=https://github.com/termux/termux-x11`
- `PACKAGE=com.termux.x11`
- `VERSION_CODE=15`
- `INSTALLED_UID=10602`
- `TERMUX_UID=10602`
- `SHARED_UID=YES`

The version and full commit are embedded in the installed APK's `classes.dex`.
Fetching the full commit from upstream succeeds. The earlier abbreviated fetch
failure was not evidence of a fork: Git does not accept an abbreviated SHA as a
remote refspec.

## Certificate and update compatibility

- `INSTALLED_TERMUX_CERT_SHA256=b6da01480eefd5fbf2cd3771b8d1021ec791304bdd6c4bf41d3faabad48ee5e1`
- `INSTALLED_X11_CERT_SHA256=b6da01480eefd5fbf2cd3771b8d1021ec791304bdd6c4bf41d3faabad48ee5e1`
- `CERTIFICATES_MATCH=YES`
- `UPDATE_REQUIRES_SAME_SIGNATURE=YES`
- `SHARED_UID_REQUIREMENT=package com.termux.x11, sharedUserId com.termux, certificate identical to com.termux`

The certificates were extracted read-only from the installed APK v2/v3 signing
blocks and retained under `state/installed-certs/`. Their byte-identical DER
certificates hash to the value above.

Upstream's shared-UID flavor declares `android:sharedUserId="com.termux"`, uses
package `com.termux.x11`, target SDK 28, versionCode 15, and signs debug builds
with `lorie-app/testkey_untrusted.jks`. The vendored keystore SHA-256 is
`a2ba19f2417de94dd3bdfb6ceece070cdc5f9b492af09cd5900058e860b18c7d`.
Termux publishes that test key's certificate fingerprint as the exact installed
`b6da...e5e1` value.

- `CAN_BUILD_INSTALLABLE_REPLACEMENT=YES`
- `WHY=The exact upstream sharedUid debug flavor uses the same public Termux GitHub test certificate, package, shared UID, and versionCode as the installed APK.`

At this historical checkpoint no APK had yet been installed, replaced, or
uninstalled. The later standalone migration is complete and supersedes that
statement.

## Source parity

- `BUILD_SOURCE_REVISION=50ac80fb2d4a475e323e752d17fcc0483c3c99fc`
- `PATCH_TARGET_REVISION=50ac80fb2d4a475e323e752d17fcc0483c3c99fc`
- `SOURCE_PARITY=PASS`

The installed APK embeds the exact full commit. Comparison against current
upstream shows `InputEventSender.java` unchanged; native translation changes
after the installed revision are refactoring only. The build branch is rooted
directly at the installed revision, so compilation does not rely on that parity
inference.

## Remote build

The workflow `.github/workflows/macdesk-s25-superfix.yml` pins:

- base source commit `50ac80fb2d4a475e323e752d17fcc0483c3c99fc`;
- Java 17;
- Android platform 34 and build-tools 34.0.0;
- NDK `29.0.14206865`;
- repository Gradle wrapper and declared dependency versions;
- immutable commit SHAs for GitHub Actions.

It runs logical unit tests, builds only the shared-UID debug APK, verifies the
resulting signing certificate and versionCode, and emits the requested APK,
checksums, and metadata. APK installation remains forbidden until the workflow
passes and downloaded artifacts are independently verified on the phone.
