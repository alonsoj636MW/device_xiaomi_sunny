#!/bin/bash
#
# SPDX-FileCopyrightText: 2016 The CyanogenMod Project
# SPDX-FileCopyrightText: 2017-2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

set -e

DEVICE=sunny
VENDOR=xiaomi

# Load extract_utils and do some sanity checks
MY_DIR="${BASH_SOURCE%/*}"
if [[ ! -d "${MY_DIR}" ]]; then MY_DIR="${PWD}"; fi

ANDROID_ROOT="${MY_DIR}/../../.."

HELPER="${ANDROID_ROOT}/tools/extract-utils/extract_utils.sh"
if [ ! -f "${HELPER}" ]; then
    echo "Unable to find helper script at ${HELPER}"
    exit 1
fi
source "${HELPER}"

# Default to sanitizing the vendor folder before extraction
CLEAN_VENDOR=true

KANG=
SECTION=

while [ "${#}" -gt 0 ]; do
    case "${1}" in
        -n | --no-cleanup )
                CLEAN_VENDOR=false
                ;;
        -k | --kang )
                KANG="--kang"
                ;;
        -s | --section )
                SECTION="${2}"; shift
                CLEAN_VENDOR=false
                ;;
        * )
                SRC="${1}"
                ;;
    esac
    shift
done

if [ -z "${SRC}" ]; then
    SRC="adb"
fi

function blob_fixup() {
    case "${1}" in
        vendor/lib64/camera/components/com.qti.node.watermark.so)
            [ "$2" = "" ] && return 0
            grep -q "libpiex_shim.so" "${2}" || "${PATCHELF}" --add-needed "libpiex_shim.so" "${2}"
            ;;
        vendor/lib64/hw/camera.qcom.so | vendor/lib64/libFaceDetectpp-0.5.2.so | vendor/lib64/libfacedet.so)
            [ "$2" = "" ] && return 0
            grep -q "libfacedet.so" "${2}" || sed -i "s|libmegface.so|libfacedet.so|g" "${2}"
            grep -q "libFaceDetectpp-0.5.2.so" "${2}" || sed -i "s|libMegviiFacepp-0.5.2.so|libFaceDetectpp-0.5.2.so|g" "${2}"
            grep -q "facedetectpp_0_5_2_model" "${2}" || sed -i "s|megviifacepp_0_5_2_model|facedetectpp_0_5_2_model|g" "${2}"
            ;;
        vendor/etc/init/android.hardware.drm@1.3-service.widevine.rc)
            [ "$2" = "" ] && return 0
            grep -q "task_profiles" "${2}" || sed -i "s|writepid /dev/cpuset/foreground/tasks|task_profiles ProcessCapacityHigh HighPerformance|g" "${2}"
            ;;
        vendor/etc/init/android.hardware.neuralnetworks@1.3-service-qti.rc)
            [ "$2" = "" ] && return 0
            grep -q "task_profiles" "${2}" || sed -i "s|writepid /dev/stune/nnapi-hal/tasks|task_profiles NNApiHALPerformance|g" "${2}"
            ;;
        vendor/lib64/mediadrm/libwvdrmengine.so|vendor/lib64/libwvhidl.so)
            [ "$2" = "" ] && return 0
            grep -q "libcrypto-v33.so" "${2}" || "${PATCHELF}" --replace-needed "libcrypto.so" "libcrypto-v33.so" "$2"
            ;;
        *)
            return 1
            ;;
    esac

    return 0
}

function blob_fixup_dry() {
    blob_fixup "$1" ""
}

# Initialize the helper
setup_vendor "${DEVICE}" "${VENDOR}" "${ANDROID_ROOT}" false "${CLEAN_VENDOR}"

extract "${MY_DIR}/proprietary-files.txt" "${SRC}" "${KANG}" --section "${SECTION}"

"${MY_DIR}/setup-makefiles.sh"
