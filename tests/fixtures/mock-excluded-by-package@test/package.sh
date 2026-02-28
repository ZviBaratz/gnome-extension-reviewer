#!/bin/bash
# Build script that excludes test files from the zip
zip -r extension.zip . --exclude "lib/MockDevice.js" "*.test.js"
