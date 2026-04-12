#!/usr/bin/env bash
set -euo pipefail

BASE_WEB="${BASE_WEB:-http://127.0.0.1:3000}"
BASE_API="${BASE_API:-http://127.0.0.1:8001/api/v1}"
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@propscrap.local}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-Admin1234}"
TEST_CUIT="${TEST_CUIT:-20294790722}"
COOKIE_USER="$(mktemp)"
COOKIE_ADMIN="$(mktemp)"
EMAIL="qa.$(date +%s)@example.com"
PASS="Admin1234!"
SOURCE_ID=""
SOURCE_SLUG=""
PYTHON_BIN="${PYTHON_BIN:-apps/api/.venv/bin/python}"

cleanup() {
  if [[ -x "$PYTHON_BIN" ]]; then
    PYTHONPATH="apps/api${PYTHONPATH:+:$PYTHONPATH}" \
    SMOKE_EMAIL="$EMAIL" \
    SMOKE_SOURCE_ID="$SOURCE_ID" \
    SMOKE_SOURCE_SLUG="$SOURCE_SLUG" \
    "$PYTHON_BIN" - <<'PY' >/dev/null 2>&1 || true
from sqlalchemy import delete, select

from app.db.session import SessionLocal
from app.models import Alert, CompanyProfile, DocumentText, Source, SourceRun, Tender, TenderDocument, TenderEnrichment, TenderMatch, TenderState, User

email = __import__("os").environ.get("SMOKE_EMAIL", "")
source_id_raw = __import__("os").environ.get("SMOKE_SOURCE_ID", "")
source_slug = __import__("os").environ.get("SMOKE_SOURCE_SLUG", "")
source_id = int(source_id_raw) if source_id_raw.isdigit() else None

db = SessionLocal()
try:
    if source_id is not None:
        tender_ids = db.execute(select(Tender.id).where(Tender.source_id == source_id)).scalars().all()
        if tender_ids:
            db.execute(delete(Alert).where(Alert.tender_id.in_(tender_ids)))
            db.execute(delete(TenderState).where(TenderState.tender_id.in_(tender_ids)))
            document_ids = db.execute(select(TenderDocument.id).where(TenderDocument.tender_id.in_(tender_ids))).scalars().all()
            if document_ids:
                db.execute(delete(DocumentText).where(DocumentText.tender_document_id.in_(document_ids)))
                db.execute(delete(TenderDocument).where(TenderDocument.id.in_(document_ids)))
            db.execute(delete(TenderEnrichment).where(TenderEnrichment.tender_id.in_(tender_ids)))
            db.execute(delete(TenderMatch).where(TenderMatch.tender_id.in_(tender_ids)))
            db.execute(delete(Tender).where(Tender.id.in_(tender_ids)))
        db.execute(delete(SourceRun).where(SourceRun.source_id == source_id))
        db.execute(delete(Source).where(Source.id == source_id))
    elif source_slug:
        db.execute(delete(Source).where(Source.slug == source_slug))

    if email:
        user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if user is not None:
            company_profile_id = user.company_profile_id
            db.execute(delete(Alert).where(Alert.user_id == user.id))
            db.execute(delete(TenderState).where(TenderState.user_id == user.id))
            db.execute(delete(User).where(User.id == user.id))
            if company_profile_id is not None:
                remaining = db.execute(
                    select(User.id).where(User.company_profile_id == company_profile_id)
                ).scalars().first()
                if remaining is None:
                    db.execute(delete(TenderMatch).where(TenderMatch.company_profile_id == company_profile_id))
                    db.execute(delete(CompanyProfile).where(CompanyProfile.id == company_profile_id))
    db.commit()
finally:
    db.close()
PY
  fi
  rm -f "$COOKIE_USER" "$COOKIE_ADMIN"
}
trap cleanup EXIT

retry_curl() {
  curl --retry 5 --retry-delay 1 --retry-connrefused --retry-all-errors "$@"
}

check_contains() {
  local url="$1"
  local needle="$2"
  local body
  body="$(retry_curl -fsS "$url")"
  if [[ "$body" != *"$needle"* ]]; then
    echo "FAIL contains: $url -> $needle" >&2
    exit 1
  fi
  echo "OK page: $url"
}

check_auth_page() {
  local cookie="$1"
  local url="$2"
  local needle="$3"
  local body
  body="$(retry_curl -fsS -b "$cookie" "$url")"
  if [[ "$body" != *"$needle"* ]]; then
    echo "FAIL auth page: $url -> $needle" >&2
    exit 1
  fi
  echo "OK auth page: $url"
}

json_first_tender_id() {
  python3 -c 'import json,sys; data=json.load(sys.stdin); items=data.get("items") or []; print(items[0]["id"] if items else "")'
}

echo "[1] health"
HEALTH="$(retry_curl -fsS http://127.0.0.1:8001/health)"
[[ "$HEALTH" == *'"status":"ok"'* ]] || { echo "FAIL health payload" >&2; exit 1; }
[[ "$HEALTH" == *'"ocr"'* ]] || { echo "FAIL health missing ocr" >&2; exit 1; }

echo "[2] public pages"
check_contains "$BASE_WEB/" "La infraestructura operativa para empresas que venden al Estado."
check_contains "$BASE_WEB/signup" "Registrá tu empresa por CUIT."
check_contains "$BASE_WEB/login" "Ingresá a tu workspace."
retry_curl -fsS "$BASE_API/public/platform-settings" >/dev/null

echo "[3] company lookup"
LOOKUP="$(retry_curl -fsS "$BASE_API/company-lookup/cuit/$TEST_CUIT")"
[[ "$LOOKUP" == *"$TEST_CUIT"* ]] || { echo "FAIL lookup" >&2; exit 1; }

echo "[4] signup user"
SIGNUP_CODE="$(retry_curl -sS -o /tmp/smoke_signup.json -w '%{http_code}' -c "$COOKIE_USER" \
  -H 'Content-Type: application/json' \
  -d "{\"full_name\":\"QA User\",\"email\":\"$EMAIL\",\"password\":\"$PASS\",\"cuit\":\"$TEST_CUIT\",\"company_name\":\"QA Empresa\"}" \
  "$BASE_API/auth/signup")"
[[ "$SIGNUP_CODE" == "200" ]] || { echo "FAIL signup code=$SIGNUP_CODE"; cat /tmp/smoke_signup.json; exit 1; }

echo "[5] me/profile/user flow"
ME="$(retry_curl -fsS -b "$COOKIE_USER" "$BASE_API/me")"
[[ "$ME" == *"$EMAIL"* ]] || { echo "FAIL me" >&2; exit 1; }
PROFILE="$(retry_curl -fsS -b "$COOKIE_USER" "$BASE_API/me/company-profile")"
[[ "$PROFILE" == *"company_name"* ]] || { echo "FAIL profile" >&2; exit 1; }

PATCH_CODE="$(retry_curl -sS -o /tmp/smoke_patch_me.json -w '%{http_code}' -b "$COOKIE_USER" \
  -H 'Content-Type: application/json' \
  -X PATCH \
  -d '{"full_name":"QA User Updated","whatsapp_number":"+5491123456789","whatsapp_opt_in":true,"email_opt_in":true,"alert_priority":"media","receive_deadlines":true,"receive_relevant":true}' \
  "$BASE_API/me")"
[[ "$PATCH_CODE" == "200" ]] || { echo "FAIL patch me=$PATCH_CODE"; cat /tmp/smoke_patch_me.json; exit 1; }

PUT_PROFILE_CODE="$(retry_curl -sS -o /tmp/smoke_put_profile.json -w '%{http_code}' -b "$COOKIE_USER" \
  -H 'Content-Type: application/json' \
  -X PUT \
  -d '{"company_name":"QA Empresa SA","legal_name":"QA Empresa SA","company_description":"Servicios y tecnologia para compras publicas","sectors":["tecnologia"],"include_keywords":["software","servicios"],"exclude_keywords":["obra civil"],"jurisdictions":["Nacion"],"preferred_buyers":["Ministerio de Economia"],"min_amount":"1000000","max_amount":"90000000","alert_preferences_json":{"min_score":60},"tax_status_json":{"iva":"responsable inscripto"}}' \
  "$BASE_API/me/company-profile")"
[[ "$PUT_PROFILE_CODE" == "200" ]] || { echo "FAIL put profile=$PUT_PROFILE_CODE"; cat /tmp/smoke_put_profile.json; exit 1; }

REMATCH_CODE="$(retry_curl -sS -o /tmp/smoke_rematch.json -w '%{http_code}' -b "$COOKIE_USER" -X POST "$BASE_API/me/company-profile/rematch")"
[[ "$REMATCH_CODE" == "200" ]] || { echo "FAIL rematch=$REMATCH_CODE"; cat /tmp/smoke_rematch.json; exit 1; }

echo "[6] tenders and saved flow"
TENDERS="$(retry_curl -fsS -b "$COOKIE_USER" "$BASE_API/tenders?min_score=0&limit=5")"
TENDER_ID="$(printf '%s' "$TENDERS" | json_first_tender_id)"
if [[ -z "$TENDER_ID" ]]; then
  echo "WARN no tenders available, skipping saved flow"
else
  STATE_CODE="$(retry_curl -sS -o /tmp/smoke_state.json -w '%{http_code}' -b "$COOKIE_USER" \
    -H 'Content-Type: application/json' \
    -X POST \
    -d '{"state":"saved","notes":"QA smoke"}' \
    "$BASE_API/tenders/$TENDER_ID/state")"
  [[ "$STATE_CODE" == "200" ]] || { echo "FAIL state=$STATE_CODE"; cat /tmp/smoke_state.json; exit 1; }
  SAVED="$(retry_curl -fsS -b "$COOKIE_USER" "$BASE_API/saved-tenders")"
  [[ "$SAVED" == *'"items"'* ]] || { echo "FAIL saved-tenders" >&2; exit 1; }
fi

USERS_COMPANY_CODE="$(retry_curl -sS -o /tmp/smoke_users_company.json -w '%{http_code}' -b "$COOKIE_USER" "$BASE_API/users")"
[[ "$USERS_COMPANY_CODE" == "200" ]] || { echo "FAIL company users=$USERS_COMPANY_CODE"; cat /tmp/smoke_users_company.json; exit 1; }

echo "[7] authenticated pages"
check_auth_page "$COOKIE_USER" "$BASE_WEB/dashboard" "Oportunidades."
check_auth_page "$COOKIE_USER" "$BASE_WEB/saved" "Pipeline."
check_auth_page "$COOKIE_USER" "$BASE_WEB/company-profile" "Perfil comercial."
check_auth_page "$COOKIE_USER" "$BASE_WEB/mi-cuenta" "Preferencias personales."
check_auth_page "$COOKIE_USER" "$BASE_WEB/admin/company" "Equipo y perfil comercial."

echo "[8] admin login"
LOGIN_CODE="$(retry_curl -sS -o /tmp/smoke_admin_login.json -w '%{http_code}' -c "$COOKIE_ADMIN" \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"$ADMIN_EMAIL\",\"password\":\"$ADMIN_PASSWORD\"}" \
  "$BASE_API/auth/login")"
[[ "$LOGIN_CODE" == "200" ]] || { echo "FAIL admin login=$LOGIN_CODE"; cat /tmp/smoke_admin_login.json; exit 1; }

for path in /users /admin/sources /admin/automation /source-runs /alerts /admin/company-profiles /admin/alerts/outbox /admin/audit-events; do
  code="$(retry_curl -sS -o /tmp/out.json -w '%{http_code}' -b "$COOKIE_ADMIN" "$BASE_API$path")"
  [[ "$code" == "200" ]] || { echo "FAIL admin GET $path code=$code"; cat /tmp/out.json; exit 1; }
  echo "OK admin GET $path"
done

SLUG="qa-source-$(date +%s)"
SOURCE_SLUG="$SLUG"
CREATE_CODE="$(retry_curl -sS -o /tmp/smoke_create_source.json -w '%{http_code}' -b "$COOKIE_ADMIN" \
  -H 'Content-Type: application/json' \
  -d "{\"name\":\"QA Source\",\"slug\":\"$SLUG\",\"source_type\":\"portal\",\"scraping_mode\":\"html\",\"connector_slug\":\"\",\"base_url\":\"https://example.com\",\"config_json\":{\"note\":\"smoke\"},\"is_active\":false}" \
  "$BASE_API/admin/sources")"
[[ "$CREATE_CODE" == "200" ]] || { echo "FAIL create source=$CREATE_CODE"; cat /tmp/smoke_create_source.json; exit 1; }

SOURCE_ID="$(python3 -c 'import json; import sys; print(json.load(open("/tmp/smoke_create_source.json"))["id"])')"
[[ -n "$SOURCE_ID" ]] || { echo "FAIL source id parse" >&2; cat /tmp/smoke_create_source.json; exit 1; }

UPDATE_CODE="$(retry_curl -sS -o /tmp/smoke_update_source.json -w '%{http_code}' -b "$COOKIE_ADMIN" \
  -H 'Content-Type: application/json' \
  -X PATCH \
  -d '{"name":"QA Source Updated","is_active":true}' \
  "$BASE_API/admin/sources/$SOURCE_ID")"
[[ "$UPDATE_CODE" == "200" ]] || { echo "FAIL update source=$UPDATE_CODE"; cat /tmp/smoke_update_source.json; exit 1; }

check_auth_page "$COOKIE_ADMIN" "$BASE_WEB/admin/platform" "Consola de plataforma."

echo "SMOKE OK"
