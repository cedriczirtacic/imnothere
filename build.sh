#!/bin/bash
OS=$(uname -s)
SITE='https://chromedriver.storage.googleapis.com'

function get_latest_version() {
    local VERSION=$(wget -q -O- "${SITE}/LATEST_RELEASE")
    if [ $? -gt 0 ];then
        echo -n '' && return
    fi
    echo $VERSION
}

if $(which chromedriver >/dev/null);then
    echo "chromedriver ($(chromedriver --version|cut -d' ' -f2)) seems to be installed."
    exit 0
fi

case $OS in
    "Darwin")
        ZIP="chromedriver_mac64.zip"
        ;;
    "Linux")
        ZIP="chromedriver_linux64.zip"
        ;;
esac
URL="https://chromedriver.storage.googleapis.com/$(get_latest_version)/${ZIP}"

wget -q -P /tmp "$URL" || { \ 
    echo "Couldn't download chromedriver!" && exit 2;
}
unzip -qq -d $(pwd) /tmp/$ZIP && rm -f /tmp/$ZIP
echo "Done! Version: $(./chromedriver --version)"
exit 0

