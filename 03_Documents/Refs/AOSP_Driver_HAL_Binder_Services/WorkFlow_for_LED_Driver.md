# Implementing a Custom HAL Service (HIDL/AIDL) for GPIO Control in AOSP 14 with Qt/QML Integration

This guide explains how to implement a **Custom HAL Service** using **HIDL/AIDL** for GPIO control on a **Qualcomm SC200E (QCM2290/QCS2290)** based AOSP 14 platform and how to access it from a **Qt/QML Android application**.

---

## ✅ Overview

A Custom HAL Service allows you to create a standardized Android service that exposes hardware functionality (GPIO in this case) to applications through Binder IPC. Your Qt/QML application will communicate with this service using JNI and Java AIDL proxy classes.

---

## 🔹 Workflow (Step-by-Step)

1. **Define the GPIO pin in the Device Tree**
2. **Provide a kernel driver or use existing GPIO interfaces**
3. **Create an AIDL/HIDL interface definition**
4. **Implement the Binder service that uses the kernel driver**
5. **Start the service automatically at boot (init.rc)**
6. **Add SELinux policy rules for the service and application**
7. **Access the service from the Qt/QML application via JNI and AIDL proxy**

---

## 🔹 Detailed Steps

### 1️⃣ Define GPIO in Device Tree

Add the GPIO pin definition in the DTS file:

```dts
led1: my_led {
    compatible = "gpio-leds";
    gpios = <&tlmm 54 GPIO_ACTIVE_HIGH>;
    default-state = "off";
};
```

This ensures that the pin is registered by the kernel.

### 2️⃣ Provide a Kernel Driver or Use Existing Interfaces

* For LED control, the **gpio-leds** driver automatically exposes `/sys/class/leds/my_led/brightness`.
* For general-purpose GPIO, either:

  * Use the **GPIO character device interface** (`/dev/gpiochipX`) with **libgpiod**.
  * Implement a **custom kernel driver** to expose a device node.

### 3️⃣ Define HIDL/AIDL Interface

Create an AIDL file in `hardware/interfaces/gpio/1.0/IGpioService.aidl`:

```aidl
package hardware.gpio;

interface IGpioService {
    void setValue(int gpio, boolean value);
    boolean getValue(int gpio);
}
```

### 4️⃣ Implement the Binder Service

Write a **C++ service binary** that implements the interface and interacts with the kernel driver or sysfs:

```cpp
class GpioService : public BnGpioService {
public:
    void setValue(int gpio, bool value) override {
        // Use gpiod or sysfs to set GPIO value
    }

    bool getValue(int gpio) override {
        // Return current GPIO value
    }
};

int main() {
    android::sp<GpioService> service = new GpioService();
    defaultServiceManager()->addService(String16("gpio_service"), service);
    android::IPCThreadState::self()->joinThreadPool();
    return 0;
}
```

### 5️⃣ Start the Service at Boot

Add to `init.rc`:

```
service gpio_service /system/bin/gpio_service
    class hal
    user system
    group system
    oneshot
```

### 6️⃣ Configure SELinux Policies

* Define a service domain (`gpio_service.te`).
* Add rules to allow the Qt app domain to find and call the service:

```
allow smartnfc_app gpio_service:service_manager find;
allow smartnfc_app gpio_service:binder call;
```

### 7️⃣ Connect from Qt/QML Application

#### Java Helper (AIDL Proxy)

```java
IGpioService service = IGpioService.Stub.asInterface(
    ServiceManager.getService("gpio_service"));
service.setValue(54, true);
```

#### JNI Bridge (QtAndroidHelper.cpp)

```cpp
void QtAndroidHelper::setLedState(bool state) {
    QJniObject javaHelper("org/qtproject/coffeeui/GpioHelper");
    javaHelper.callMethod<void>("setLedState", "(Z)V", state);
}
```

#### QML Usage

```qml
Button {
    text: "LED ON"
    onClicked: QtAndroidHelper.setLedState(true)
}
```

---

## ✅ Advantages

✔ Follows Android standards (Binder IPC, HAL layer)
✔ Clean SELinux handling (application does not need sysfs permissions)
✔ Reusable for multiple apps and hardware features
✔ Scalable to other peripherals (I2C, SPI, etc.)

---

## ❌ Disadvantages

✘ More complex (HAL + Service + SELinux + JNI)
✘ Requires AOSP build integration
✘ Overkill for single-app prototypes

---

## 📌 Recommended Use Cases

* Long-term product development
* Multi-application hardware access
* When following Android security/architecture best practices is required

---

## 📂 Example Project Structure

```
hardware/interfaces/gpio/1.0/IGpioService.aidl
system/core/gpio_service/gpio_service.cpp
system/core/gpio_service/Android.bp
system/sepolicy/private/gpio_service.te
init/init.rc
```

---

## 📌 Qt Integration Flow

```
QML → C++ (QtAndroidHelper) → JNI → Java (AIDL Proxy) → Binder → gpio_service → Kernel Driver
```
