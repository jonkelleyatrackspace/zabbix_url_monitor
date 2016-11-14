#!/bin/bash
# vim: set fileencoding=utf-8 :

# This script bumps version in a RPM specfile present in the working directory.
# It takes a version argument and that version is than used to override the old one.
#
# Usage:
#  ./rpm-bump-version 1.0.0

# Useful ansi color code
RESTORE='\033[0m'
RED='\033[00;31m'
LGREEN='\033[01;32m'

NEW=$1
SPEC=`ls *spec`
RELEASE="1" # hard code

if [ -z ${AUTHOR} ]; then
    echo "What is your name? [first last]"
    read AUTHOR
fi
if [ -z ${EMAIL} ]; then
    echo "What is your email? [user@host]"
    read EMAIL
fi

echo "${0}: Performing versioning tasks..."
echo -e "${LBLUE}Make Release: ${NEW}"

# -------------------------------------------------------------
# RPM SPEC
# -------------------------------------------------------------
echo -en "${LGREEN}"
echo "   * Re-writing  \`${SPEC}\`"
echo -en "${RESTORE}"

echo -en "${RED}"
sed -i -e "s/Version:\([ ]*\).*/Version:\1$NEW/g" "$SPEC"
sed -i -e "s/Release:\([ ]*\).*/Release:\11%{?dist}/g" "$SPEC"

SPEC_CHANGELOG='* '
SPEC_CHANGELOG+=`date +'%a %b %d %Y'`
SPEC_CHANGELOG+=" ${AUTHOR} <${EMAIL}> - ${NEW}-1\n"
SPEC_CHANGELOG+="- New Version ${NEW}"

sed -i -e "s/%changelog/%changelog\n$SPEC_CHANGELOG\n/g" "$SPEC" 
echo -en "${RESTORE}"
echo -en "${RED}"

# -------------------------------------------------------------
# CHANGELOG.md template
# -------------------------------------------------------------
cat << EOF >> CHANGELOG.md.template
## Version ${NEW}-1 (`date +'%a %b %d %Y'`) @${AUTHOR}


<<<<<<<<<EDIT THIS TEMPLATE BEFORE COMMITING CHANGES>>>>>>>>>


New feature:

* Feature description

Bugfix

* Fix 1
* Fix 2

Improvements

* Improved performance of x
* Improved file mapping resolution
* Refactored class messyClass

Doc Update
* Added section about new feature Y
\n
-----
\n
EOF
echo -en "${RESTORE}"

# ---------

echo -en "${LGREEN}"
echo "   * Re-writing  \`CHANGELOG.md\`"
echo -en "${RESTORE}"

echo -en "${RED}"
echo -e "$(cat CHANGELOG.md.template)\n$(cat CHANGELOG.md)" > CHANGELOG.md
rm CHANGELOG.md.template
echo -en "${RESTORE}"

# -------------------------------------------------------------
# url_monitor/__init__.py
# -------------------------------------------------------------
echo -en "${LGREEN}"
echo "   * Re-writing  \`__init__.py\`"
echo -en "${RESTORE}"

# Perform sed
echo -en "${RED}"
sed -i -e "s/__version__ = \"\([ ]*\).*\"/__version__ = \"\1$NEW\"/g"  "url_monitor/__init__.py" 
echo -en "${RESTORE}"

# -------------------------------------------------------------
# setup.py
# -------------------------------------------------------------
echo -en "${LGREEN}"
echo "   * Re-writing  \`setup.py\`"
echo -en "${RESTORE}"

# Perform sed
echo -en "${RED}"
sed -i -e "s/^        version=\"\([ ]*\).*\",/        version=\"\1$NEW\",/g"  "setup.py"
echo -en "${RESTORE}"


