#!/bin/bash

set -e

INSTALL_PATH=/opt/firestation
WHEEL_FILE=/tmp/firestation_gateway-0.1.0-py3-none-any.whl
SYSTEMD_USER="www-data"
CFG_FILE=0

PACKAGE_NAME="firestation-gateway"
SCRIPT_NAME="firestation-gw"

SERVICE_NAME="$PACKAGE_NAME.service"
SERVICE_PATH=/etc/systemd/system/$SERVICE_NAME

WEB_SITE_CONFIG_PATH=/etc/apache2/sites-available/gw.$(hostname).local.conf


setup_systemd_service() {
  sh -c 'cat <<EOF > '$SERVICE_PATH'
[Unit]
Description=Firestation Gateway
After=network.target

[Service]
WorkingDirectory={{PROJECT_PATH}}
ExecStart={{PROJECT_PATH}}/venv/bin/{{SCRIPT_NAME}}
Restart=always
User={{SYSTEMD_USER}}

[Install]
WantedBy=multi-user.target
EOF'

  sed -i \
          -e "s|{{SYSTEMD_USER}}|$SYSTEMD_USER|g" \
          -e "s|{{PROJECT_PATH}}|$INSTALL_PATH|g" \
          -e "s|{{SCRIPT_NAME}}|$SCRIPT_NAME|g" \
          "$SERVICE_PATH"

  systemctl daemon-reload
  systemctl enable --now "$SERVICE_NAME"
  systemctl restart "$SERVICE_NAME"
  echo "[INFO] systemd Dienst aktiviert: $SERVICE_NAME"
}

setup_web_service() {
  echo "web"
  # check webserver dependency
  command -v apache2 > /dev/null || apt-get install -y apache2
  
  command -v php > /dev/null || apt-get install -y php
  command -v php-symfony-yaml > /dev/null || apt-get install -y php-symfony-yaml
  command -v php-yaml > /dev/null || apt-get install -y php-yaml

  command -v libapache2-mod-php > /dev/null || apt-get install -y libapache2-mod-php
  service apache2 restart

  # copy site config
  sh -c 'cat <<EOF > '$WEB_SITE_CONFIG_PATH'
Listen 8080
<VirtualHost *:8080>
    ServerName gw.'$(hostname)'.local
    DocumentRoot "'$INSTALL_PATH'/web"
    <Directory '$INSTALL_PATH'/web>
        AllowOverride None
        Require all granted
    </Directory>

</VirtualHost>
EOF'
  # disable default site
  a2dissite 000-default.conf 
  # restart webserver
  a2ensite $(basename ${WEB_SITE_CONFIG_PATH})
  service apache2 reload

  # web-frontend need this
  # TODO: find a better solution for this
  sh -c 'cat <<EOF > /etc/sudoers.d/99-firestation-web
www-data ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart '$SERVICE_NAME'
www-data ALL=(ALL) NOPASSWD: /usr/bin/journalctl -u '$SERVICE_NAME' -n 20 --no-pager
EOF'

}

setup_fsg() {

  mkdir -p $INSTALL_PATH

  chown -R $SYSTEMD_USER $INSTALL_PATH

  # run next commands as $SYSTEMD_USER user
  sudo -su $SYSTEMD_USER

  cd $INSTALL_PATH

  python3 -m venv "$INSTALL_PATH/venv"
  . "$INSTALL_PATH/venv/bin/activate"
  pip install --upgrade pip

  pip install "$WHEEL_FILE"

  if [[ $CFG_FILE -ne 0 ]]; then
      echo "[INFO] Installiere Konfigurationsdatei $CFG_FILE"
      cp -v $CFG_FILE $INSTALL_PATH/config.yaml
  else
      echo "[INFO] Generiere Beispielkonfiguration"
      firestation-gw --generate-config > $INSTALL_PATH/config.yaml
  fi
  # exit $SYSTEMD_USER
  exit 0

  sudo chown $SYSTEMD_USER:www-data $INSTALL_PATH/config.yaml
  # sudo chown -R $SYSTEMD_USER $INSTALL_PATH
  
  # user need access to gpio
  sudo usermod -aG gpio $SYSTEMD_USER
}

main() {
  # --- Argumente parsen ---
  while [[ "$#" -gt 0 ]]; do
      case $1 in
          --install-dir) INSTALL_PATH="$2"; shift ;;
          --user) SYSTEMD_USER="$2"; shift ;;
          --config) CFG_FILE="$2"; shift ;;
          *) echo "Unbekannter Parameter: $1"; exit 1 ;;
      esac
      shift
  done
  # make sure package repos are up to date
  apt-get update

  # check python dependency
  command -v python3 > /dev/null || apt-get install -y python3

  # check python venv dependency
  apt-get install -y python3-venv

  setup_fsg

  setup_systemd_service

  setup_web_service

}

main "$@"