ORG="${ORG:-int_org}"
BUCKET="${BUCKET:-int_bucket}"
USERNAME="${USERNAME:-int_user}"
PASSWORD="${PASSWORD:-int_password}"
TOKEN="${ADMIN_TOKEN:-int_token}" 

influx setup \
  --username ${USERNAME} \
  --password ${PASSWORD} \
  --token ${TOKEN} \
  --org ${ORG} \
  --bucket ${BUCKET} \
  --force

influx config create \
  --config-name int_config \
  --host-url http://localhost:8086 \
  --org ${ORG} \
  --token ${TOKEN} 