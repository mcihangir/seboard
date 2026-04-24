# LED Control Service – AIDL + Binder Service (Without HAL)

This document describes how we implemented a simple LED control service for Android using AIDL and Binder, without a full HAL layer.

---

## 1️⃣ AIDL Interface

**File:** `vendor/empa/smartnfc/aidl/android/hardware/smartnfc/ISmartLed.aidl`

```aidl
package android.hardware.smartnfc;

interface ISmartLed {
    void setLedState(String ledName, int state); // 0=off, 1=on
    int getLedState(String ledName);             // returns current state
}
```

---

## 2️⃣ Service Class

**File:** `vendor/empa/smartnfc/aidl/SmartLedService.h`

```cpp
#pragma once
#include <aidl/android/hardware/smartnfc/BnSmartLed.h>

namespace aidl::android::hardware::smartnfc {

class SmartLedService : public BnSmartLed {
public:
    SmartLedService() = default;
    ~SmartLedService() override = default;

    ndk::ScopedAStatus setLedState(const std::string& ledName, int state) override;
    ndk::ScopedAStatus getLedState(const std::string& ledName, int* _aidl_return) override;
};

}  // namespace aidl::android::hardware::smartnfc
```

**File:** `vendor/empa/smartnfc/aidl/SmartLedService.cpp`

```cpp
#include "SmartLedService.h"
#include <fstream>

namespace aidl::android::hardware::smartnfc {

ndk::ScopedAStatus SmartLedService::setLedState(const std::string& ledName, int state) {
    std::string path = "/sys/class/leds/" + ledName + "/brightness";
    std::ofstream file(path);
    if (!file.is_open()) {
        return ndk::ScopedAStatus::fromServiceSpecificError(-1);
    }
    file << (state ? "1" : "0");
    return ndk::ScopedAStatus::ok();
}

ndk::ScopedAStatus SmartLedService::getLedState(const std::string& ledName, int* _aidl_return) {
    std::string path = "/sys/class/leds/" + ledName + "/brightness";
    std::ifstream file(path);
    if (!file.is_open()) {
        *_aidl_return = -1;
        return ndk::ScopedAStatus::fromServiceSpecificError(-1);
    }
    file >> *_aidl_return;
    return ndk::ScopedAStatus::ok();
}

} // namespace aidl::android::hardware::smartnfc
```

---

## 3️⃣ Service Main Program

**File:** `vendor/empa/smartnfc/aidl/smartled_service.cpp`

```cpp
#include "SmartLedService.h"
#include <android/binder_manager.h>
#include <android/binder_process.h>

using aidl::android::hardware::smartnfc::SmartLedService;

int main() {
    ABinderProcess_setThreadPoolMaxThreadCount(0);
    std::shared_ptr<SmartLedService> service = ndk::SharedRefBase::make<SmartLedService>();

    const std::string instance = std::string() + SmartLedService::descriptor + "/default";
    AServiceManager_addService(service->asBinder().get(), instance.c_str());

    ABinderProcess_joinThreadPool();
    return 0;
}
```

---

## 4️⃣ Android.bp and init.rc

**File:** `vendor/empa/smartnfc/aidl/Android.bp`

```bp
cc_binary {
    name: "smartled_service",
    srcs: [
        "smartled_service.cpp",
        "SmartLedService.cpp",
    ],
    shared_libs: [
        "libbinder_ndk",
        "libbase",
    ],
    init_rc: ["smartled_service.rc"],
    vendor: true,
}
```

**File:** `vendor/empa/smartnfc/aidl/smartled_service.rc`

```rc
service smartled_service /vendor/bin/smartled_service
    class hal
    user system
    group system

on property:sys.boot_completed=1
    start smartled_service
```

---

## 5️⃣ SELinux Policy

**File:** `vendor/empa/smartnfc/sepolicy/smartled_service.te`

```te
type smartled_service, domain;
type smartled_service_exec, exec_type, vendor_file_type, file_type;

init_daemon_domain(smartled_service)

allow smartled_service sysfs_leds:dir search;
allow smartled_service sysfs_leds:file rw_file_perms;
```

**File:** `vendor/empa/smartnfc/sepolicy/file_contexts`

```
/vendor/bin/smartled_service     u:object_r:smartled_service_exec:s0
/sys/class/leds(/.*)?            u:object_r:sysfs_leds:s0
```

---

## 6️⃣ Build and Run

```bash
m smartled_service
adb push out/target/product/<device>/vendor/bin/smartled_service /vendor/bin/
adb shell chmod 755 /vendor/bin/smartled_service
adb shell /vendor/bin/smartled_service &
```

---

## 7️⃣ Verify Binder Service

```bash
adb shell ps -A | grep smartled
adb shell lshal | grep smartnfc
adb shell service list | grep smartnfc
```

If the binder service is visible, the next step will be integrating it with Qt/QML via JNI.
