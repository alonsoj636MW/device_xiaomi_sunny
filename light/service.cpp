/*
 * Copyright (C) 2021-2024 The LineageOS Project
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#include "Lights.h"

#define LOG_TAG "android.hardware.light-service.sunny"

#include <android-base/logging.h>
#include <android/binder_manager.h>
#include <android/binder_process.h>

using ::aidl::android::hardware::light::Lights;

int main() {
    ABinderProcess_setThreadPoolMaxThreadCount(0);
    std::shared_ptr<Lights> lights = ndk::SharedRefBase::make<Lights>();

    const std::string instance = std::string() + Lights::descriptor + "/default";
    binder_status_t status = AServiceManager_addService(lights->asBinder().get(), instance.c_str());
    CHECK(status == STATUS_OK);

    ABinderProcess_joinThreadPool();
    return EXIT_FAILURE;  // should not reach
}
