#!/bin/sh
# Edit site.html, then run ./build.sh to regenerate index.html for hosting.
cd "$(dirname "$0")" && python3 -c "
s=open('site.html').read()
open('index.html','w').write('<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n</head>\n<body>\n'+s+'\n</body>\n</html>\n')"
