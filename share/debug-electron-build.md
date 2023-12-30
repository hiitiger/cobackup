## Preparations:

0. Make sure you can build Release/testing according to the official documentation.

1. Add the `build/args/debug.gn` file, 
which will contain the relevant configuration information for Debug builds.

```
import("all.gn")
is_debug = true
is_component_build = true
is_component_ffmpeg = true
is_official_build = false
dcheck_always_on = true
symbol_level = 2

# This may be guarded behind is_chrome_branded alongside
# proprietary_codecs https://webrtc-review.googlesource.com/c/src/+/36321,
# explicitly override here to build OpenH264 encoder/FFmpeg decoder.
# The initialization of the decoder depends on whether ffmpeg has
# been built with H.264 support.
rtc_use_h264 = proprietary_codecs

```


2. Make "component_build" and "node" link statically.

In `electron/build.gn``, comment out the NODE_SHARED_MODE macro definition.
In `third_party/electron_node/BUILD.gn`, comment out the NODE_SHARED_MODE macro definition.

3. zlib change

In `third_party/zlib/BUILD.gn`, add the condition `!is_component_build` to the ZLIB_DLL macro definition.

4. At this point, you can already configure for debug.

```sh
gn gen out/Debug --args="import(\"//electron/build/args/debug.gn\")" --ide=vs2022
```

## Build and fix link errors.
When building with "ninja -C out/Debug electron", you may encounter various errors.

5. There is usually an issue with exporting symbols from abseil-cpp. We need to update its `symbols_{cpu}_dbg.def ` file. Follow these steps:

First, generate the project.

```sh
ninja -C out/Debug third_party/abseil-cpp:absl_component_deps
```

Then, modify `third_party/abseil-cpp/generate_def_files.py` to generate only the def file we need, and comment out the gn gen and ninja execution.

Finally, run:

```sh
python3 "third_party/abseil-cpp/generate_def_files.py"
```

6. Fix missing dependencies. In electron/build.gn, add dependencies to "electron_lib". Please add the modifications specific to the version you are using. Below are the modifications for the 22-x-y branch:

 "//components/enterprise/common/proto:download_item_reroute_info_proto",
 "//services/cert_verifier/public/mojom",

7. Fix duplicate symbol errors for mojom.

In `electron/shell/services/node/public/mojom/BUILD.gn`:

```gn
    # Needed for component build or we'll get duplicate symbols for many mojom
    # interfaces already included in blink_common.dll
    overridden_deps = [ "//third_party/blink/public/mojom:mojom_core" ]
    component_deps = [ "//third_party/blink/public/common" ]
```

8. Fix other symbol errors.

Fix them one by one as you encounter the linking errors. Most likely, it will involve adding `CONTENT_EXPORT` decoration to some APIs in the content module that Electron is using.

9. You are good to go now