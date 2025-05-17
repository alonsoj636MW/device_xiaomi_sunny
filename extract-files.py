#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

from extract_utils.fixups_blob import (
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.fixups_lib import (
    lib_fixups,
    lib_fixups_user_type,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)

namespace_imports = [
    'device/xiaomi/sunny',
    'hardware/qcom-caf/sm8150',
    'hardware/qcom-caf/wlan',
    'hardware/xiaomi',
    'vendor/qcom/common/vendor/adreno-r',
    'vendor/qcom/common/vendor/perf',
    'vendor/qcom/opensource/dataservices',
    'vendor/qcom/opensource/display',
]


def lib_fixup_vendor_suffix(lib: str, partition: str, *args, **kwargs):
    return f'{lib}_{partition}' if partition == 'vendor' else None


lib_fixups: lib_fixups_user_type = {
    **lib_fixups,
    (
        'com.qualcomm.qti.dpm.api@1.0',
        'vendor.qti.hardware.fm@1.0',
        'vendor.qti.imsrtpservice@3.0',
    ): lib_fixup_vendor_suffix,
}

blob_fixups: blob_fixups_user_type = {
    'vendor/etc/init/android.hardware.drm@1.3-service.widevine.rc': blob_fixup()
        .regex_replace('writepid /dev/cpuset/foreground/tasks', 'task_profiles ProcessCapacityHigh HighPerformance'),
    'vendor/etc/init/android.hardware.neuralnetworks@1.3-service-qti.rc': blob_fixup()
        .regex_replace('writepid /dev/stune/nnapi-hal/tasks', 'task_profiles NNApiHALPerformance'),
    'vendor/lib64/camera/components/com.qti.node.watermark.so': blob_fixup()
        .add_needed('libpiex_shim.so'),
    ('vendor/lib64/hw/camera.qcom.so', 'vendor/lib64/libFaceDetectpp-0.5.2.so', 'vendor/lib64/libfacedet.so'): blob_fixup()
        .binary_regex_replace(b'libmegface.so', b'libfacedet.so')
        .binary_regex_replace(b'libMegviiFacepp-0.5.2.so', b'libFaceDetectpp-0.5.2.so')
        .binary_regex_replace(b'megviifacepp_0_5_2_model', b'facedetectpp_0_5_2_model'),
    ('vendor/lib64/mediadrm/libwvdrmengine.so', 'vendor/lib64/libwvhidl.so'): blob_fixup()
        .add_needed('libcrypto_shim.so'),
    ('vendor/lib64/libalLDC.so', 'vendor/lib64/libalhLDC.so'): blob_fixup()
        .clear_symbol_version('AHardwareBuffer_allocate')
        .clear_symbol_version('AHardwareBuffer_describe')
        .clear_symbol_version('AHardwareBuffer_lock')
        .clear_symbol_version('AHardwareBuffer_release')
        .clear_symbol_version('AHardwareBuffer_unlock'),
    ('vendor/lib64/libhvx_interface.so', 'vendor/lib64/libmialgo_rfs.so', 'vendor/lib64/libVDSuperPhotoAPI.so'): blob_fixup()
        .clear_symbol_version('remote_handle_close')
        .clear_symbol_version('remote_handle_invoke')
        .clear_symbol_version('remote_handle_open')
        .clear_symbol_version('remote_register_buf_attr')
        .clear_symbol_version('remote_register_buf'),
    'vendor/lib64/android.hardware.camera.provider@2.4-legacy.so': blob_fixup()
        .add_needed('libcamera_provider_shim.so')
}  # fmt: skip

module = ExtractUtilsModule(
    'sunny',
    'xiaomi',
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
    namespace_imports=namespace_imports,
)

if __name__ == '__main__':
    utils = ExtractUtils.device(module)
    utils.run()
