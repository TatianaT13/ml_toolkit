#!/bin/bash
# ============================================================
# Setup Keycloak pour ML Toolkit
# Configure automatiquement : Realm, Client, MFA, Rôles, Users
# Usage: bash scripts/setup_keycloak.sh
# ============================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

ok()   { echo -e "${GREEN}✅ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
err()  { echo -e "${RED}❌ $1${NC}"; }

KEYCLOAK_URL="http://localhost:8180"
REALM="ml-toolkit"
ADMIN_USER=${KEYCLOAK_ADMIN_USER:-admin}
ADMIN_PASS=${KEYCLOAK_ADMIN_PASSWORD:-admin}

echo "🔐 Configuration Keycloak pour ML Toolkit"
echo "=========================================="

# ─── 1. Attendre que Keycloak soit prêt ─────────────────
echo ""
info "1/6 - Attente de Keycloak..."

for i in {1..30}; do
    if curl -sf "$KEYCLOAK_URL/health/ready" > /dev/null 2>&1; then
        ok "Keycloak est prêt!"
        break
    fi
    echo -n "."
    sleep 3
done

# ─── 2. Obtenir le token admin ───────────────────────────
echo ""
info "2/6 - Authentification admin..."

TOKEN=$(curl -sf -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
    -d "client_id=admin-cli" \
    -d "username=$ADMIN_USER" \
    -d "password=$ADMIN_PASS" \
    -d "grant_type=password" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

if [ -z "$TOKEN" ]; then
    err "Impossible d'obtenir le token admin"
    exit 1
fi
ok "Token admin obtenu"

# ─── Helpers ─────────────────────────────────────────────
kc_post() { curl -sf -X POST "$KEYCLOAK_URL$1" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "$2"; }
kc_put()  { curl -sf -X PUT  "$KEYCLOAK_URL$1" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "$2"; }
kc_get()  { curl -sf "$KEYCLOAK_URL$1" -H "Authorization: Bearer $TOKEN"; }

# ─── 3. Créer le Realm ───────────────────────────────────
echo ""
info "3/6 - Configuration du Realm..."

kc_post "/admin/realms" '{
    "realm": "ml-toolkit",
    "displayName": "ML Toolkit - Malware Detection",
    "enabled": true,
    "sslRequired": "external",
    "registrationAllowed": false,
    "loginWithEmailAllowed": true,
    "duplicateEmailsAllowed": false,
    "resetPasswordAllowed": true,
    "editUsernameAllowed": false,
    "bruteForceProtected": true,
    "permanentLockout": false,
    "maxFailureWaitSeconds": 900,
    "minimumQuickLoginWaitSeconds": 60,
    "waitIncrementSeconds": 60,
    "quickLoginCheckMilliSeconds": 1000,
    "maxDeltaTimeSeconds": 43200,
    "failureFactor": 5,
    "passwordPolicy": "length(12) and upperCase(1) and lowerCase(1) and digits(1) and specialChars(1)",
    "accessTokenLifespan": 300,
    "ssoSessionIdleTimeout": 1800,
    "ssoSessionMaxLifespan": 36000
}' 2>/dev/null || warn "Realm existe déjà"

ok "Realm 'ml-toolkit' configuré"

# ─── 4. Activer MFA obligatoire ──────────────────────────
echo ""
info "4/6 - Configuration MFA..."

# Activer OTP comme requis
kc_put "/admin/realms/$REALM" '{
    "otpPolicyType": "totp",
    "otpPolicyAlgorithm": "HmacSHA1",
    "otpPolicyDigits": 6,
    "otpPolicyPeriod": 30,
    "otpPolicyInitialCounter": 0,
    "otpSupportedApplications": ["FreeOTP", "Google Authenticator", "Microsoft Authenticator", "Authy"]
}' 2>/dev/null

ok "MFA TOTP configuré (compatible Google/Microsoft Authenticator)"

# ─── 5. Créer les Clients ────────────────────────────────
echo ""
info "5/6 - Création des clients..."

# Client API
API_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
kc_post "/admin/realms/$REALM/clients" "{
    \"clientId\": \"ml-api\",
    \"name\": \"ML Toolkit API\",
    \"enabled\": true,
    \"clientAuthenticatorType\": \"client-secret\",
    \"secret\": \"$API_SECRET\",
    \"standardFlowEnabled\": false,
    \"directAccessGrantsEnabled\": true,
    \"serviceAccountsEnabled\": true,
    \"protocol\": \"openid-connect\",
    \"publicClient\": false
}" 2>/dev/null || warn "Client ml-api existe déjà"

# Client Streamlit
STREAMLIT_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
kc_post "/admin/realms/$REALM/clients" "{
    \"clientId\": \"ml-streamlit\",
    \"name\": \"ML Toolkit UI\",
    \"enabled\": true,
    \"clientAuthenticatorType\": \"client-secret\",
    \"secret\": \"$STREAMLIT_SECRET\",
    \"standardFlowEnabled\": true,
    \"directAccessGrantsEnabled\": true,
    \"redirectUris\": [\"http://localhost:8501/*\"],
    \"webOrigins\": [\"http://localhost:8501\"],
    \"protocol\": \"openid-connect\",
    \"publicClient\": false
}" 2>/dev/null || warn "Client ml-streamlit existe déjà"

ok "Clients API et Streamlit créés"

# ─── 6. Créer les Rôles et Users ─────────────────────────
echo ""
info "6/6 - Création des rôles et utilisateurs..."

# Rôles
for role in "admin" "analyst" "viewer"; do
    kc_post "/admin/realms/$REALM/roles" "{\"name\": \"$role\"}" 2>/dev/null || true
done
ok "Rôles créés: admin, analyst, viewer"

# Utilisateur admin par défaut
ADMIN_PASSWORD=$(python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits + '!@#') for _ in range(16)))")

kc_post "/admin/realms/$REALM/users" "{
    \"username\": \"mltoolkit-admin\",
    \"email\": \"admin@mltoolkit.com\",
    \"firstName\": \"Admin\",
    \"lastName\": \"MLToolkit\",
    \"enabled\": true,
    \"emailVerified\": true,
    \"requiredActions\": [\"CONFIGURE_TOTP\"],
    \"credentials\": [{
        \"type\": \"password\",
        \"value\": \"$ADMIN_PASSWORD\",
        \"temporary\": false
    }]
}" 2>/dev/null || warn "User admin existe déjà"

ok "Utilisateur admin créé"

# ─── Mettre à jour .env avec les secrets ────────────────
if [ -f .env ]; then
    sed -i.bak "s/KEYCLOAK_CLIENT_SECRET=.*/KEYCLOAK_CLIENT_SECRET=$API_SECRET/" .env 2>/dev/null || \
        echo "KEYCLOAK_CLIENT_SECRET=$API_SECRET" >> .env
    sed -i.bak "s/KEYCLOAK_STREAMLIT_SECRET=.*/KEYCLOAK_STREAMLIT_SECRET=$STREAMLIT_SECRET/" .env 2>/dev/null || \
        echo "KEYCLOAK_STREAMLIT_SECRET=$STREAMLIT_SECRET" >> .env
    rm -f .env.bak
    ok ".env mis à jour avec les secrets Keycloak"
fi

# ─── Résumé ──────────────────────────────────────────────
echo ""
echo "=========================================="
ok "Keycloak configuré avec succès!"
echo ""
echo "📋 Informations de connexion:"
echo "  ┌─ Admin Keycloak ─────────────────────────"
echo "  │  URL:      http://localhost:8180/admin"
echo "  │  Realm:    master"
echo "  │  User:     $ADMIN_USER"
echo "  │  Password: $ADMIN_PASS"
echo "  │"
echo "  ├─ ML Toolkit Admin ───────────────────────"
echo "  │  URL:      http://localhost:8501"
echo "  │  User:     mltoolkit-admin"
echo "  │  Password: $ADMIN_PASSWORD"
echo "  │  ⚠️  MFA requis au premier login!"
echo "  │"
echo "  ├─ API Client Secret ──────────────────────"
echo "  │  Secret:   ${API_SECRET:0:20}..."
echo "  │"
echo "  └─ Streamlit Client Secret ────────────────"
echo "     Secret:   ${STREAMLIT_SECRET:0:20}..."
echo ""
echo "📱 Pour configurer le MFA:"
echo "  1. Connectez-vous sur http://localhost:8501"
echo "  2. Scannez le QR code avec Google/Microsoft Authenticator"
echo "  3. Entrez le code à 6 chiffres"
echo "  4. Vous êtes sécurisé ! 🎉"
echo ""
warn "IMPORTANT: Sauvegardez le mot de passe admin: $ADMIN_PASSWORD"
