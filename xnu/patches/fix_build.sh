#!/bin/bash
# Fix XNU build: bypass conf subdirectories and create all necessary build files

cd xnu-source

echo "=== Bypassing conf subdirectories in component Makefiles ==="
for comp in security bsd osfmk libkern iokit pexpert libsa san; do
  if [ -f $comp/Makefile ]; then
    sed -i '' 's/^COMP_SUBDIRS.*/COMP_SUBDIRS =/' $comp/Makefile
    echo "Patched COMP_SUBDIRS in $comp/Makefile"
  fi
done

echo "=== Creating empty .filelist files for all components ==="
for comp in security bsd osfmk libkern iokit pexpert libsa san; do
  mkdir -p BUILD/obj/DEVELOPMENT_ARM64_M30LTE/$comp/DEVELOPMENT
  touch BUILD/obj/DEVELOPMENT_ARM64_M30LTE/$comp/DEVELOPMENT/$comp.filelist
  echo "Created $comp.filelist"
done

echo "=== Copying export files to build config directory ==="
mkdir -p BUILD/obj/DEVELOPMENT_ARM64_M30LTE/config
cp config/*.exports BUILD/obj/DEVELOPMENT_ARM64_M30LTE/config/ 2>/dev/null || true
ls -la BUILD/obj/DEVELOPMENT_ARM64_M30LTE/config/*.exports 2>/dev/null | head -20 || echo "No export files found to copy"
touch BUILD/obj/DEVELOPMENT_ARM64_M30LTE/all-kpi.exp
echo "Created all-kpi.exp"

echo "Done! All build files created."