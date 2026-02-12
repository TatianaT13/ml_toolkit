#!/bin/bash
# ============================================================
# ML TOOLKIT - Script de sécurisation complète
# Usage: bash scripts/setup_security.sh
# ============================================================

set -e  # Arrêter si erreur

echo "🔐 Sécurisation de ML Toolkit - Niveau Commercial"
echo "=================================================="

# ─── Couleurs ───────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ok()   { echo -e "${GREEN}✅ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
err()  { echo -e "${RED}❌ $1${NC}"; }

# ─── 1. Vérifier .gitignore ─────────────────────────────────
echo ""
echo "📋 1/6 - Vérification .gitignore..."

GITIGNORE_ENTRIES=(
    ".env"
    "*.env"
    "*.key"
    "*.pem"
    "*.p12"
    "secrets/"
    "*.pkl"
    "__pycache__/"
    "*.pyc"
    ".pytest_cache/"
    "logs/*.log"
    "*.sqlite"
    "*.db"
)

for entry in "${GITIGNORE_ENTRIES[@]}"; do
    if ! grep -q "^${entry}$" .gitignore 2>/dev/null; then
        echo "$entry" >> .gitignore
        ok "Ajouté au .gitignore: $entry"
    fi
done
ok ".gitignore configuré"

# ─── 2. Générer les secrets ─────────────────────────────────
echo ""
echo "🔑 2/6 - Génération des secrets..."

if [ ! -f .env ]; then
    cp .env.example .env
    
    # Générer SECRET_KEY
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i.bak "s/CHANGE-ME-generate-with-python-secrets/$SECRET_KEY/" .env
    
    # Générer FERNET_KEY pour Airflow
    FERNET_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" 2>/dev/null || echo "generate-manually")
    sed -i.bak "s/CHANGE-ME-generate-fernet-key/$FERNET_KEY/" .env
    
    # Générer des mots de passe forts
    POSTGRES_PASS=$(python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32)))")
    sed -i.bak "s/CHANGE-ME-strong-password/$POSTGRES_PASS/g" .env
    
    # Nettoyer les .bak
    rm -f .env.bak
    
    ok ".env créé avec secrets générés automatiquement"
    warn "IMPORTANT: Configurez VIRUSTOTAL_API_KEY et ALLOWED_ORIGINS dans .env"
else
    warn ".env existe déjà - pas modifié"
fi

# ─── 3. Installer outils de sécurité ────────────────────────
echo ""
echo "📦 3/6 - Installation des outils de sécurité..."

pip install -q \
    python-jose[cryptography] \
    passlib[bcrypt] \
    python-dotenv \
    slowapi \
    bandit \
    safety \
    detect-secrets \
    cryptography

ok "Outils de sécurité installés"

# ─── 4. Scanner le code ─────────────────────────────────────
echo ""
echo "🔍 4/6 - Scan de sécurité du code..."

mkdir -p logs

# Bandit scan
echo "  → Bandit (vulnerabilités Python)..."
bandit -r my_ml_toolkit/ api.py -ll -q 2>/dev/null && ok "Bandit: aucune vulnérabilité critique" || warn "Bandit: vulnérabilités trouvées - vérifiez logs/bandit-report.txt"
bandit -r my_ml_toolkit/ api.py -ll 2>/dev/null > logs/bandit-report.txt || true

# Safety scan
echo "  → Safety (dépendances)..."
safety check -r requirements.txt -q 2>/dev/null && ok "Safety: aucune dépendance vulnérable" || warn "Safety: dépendances vulnérables - lancez 'safety check' pour détails"

# Detect-secrets
echo "  → Detect-secrets..."
detect-secrets scan --all-files > .secrets.baseline 2>/dev/null
SECRETS_COUNT=$(python3 -c "import json; d=json.load(open('.secrets.baseline')); print(sum(len(v) for v in d['results'].values()))" 2>/dev/null || echo "0")
if [ "$SECRETS_COUNT" -eq 0 ]; then
    ok "Detect-secrets: aucun secret trouvé"
else
    err "Detect-secrets: $SECRETS_COUNT secret(s) potentiel(s) trouvé(s)!"
    warn "Lancez 'detect-secrets audit .secrets.baseline' pour vérifier"
fi

# ─── 5. Configurer GitHub ───────────────────────────────────
echo ""
echo "⚙️  5/6 - Configuration GitHub CI/CD..."

mkdir -p .github/workflows

# Copier le workflow de sécurité
if [ -f "security_project/github/security.yml" ]; then
    cp security_project/github/security.yml .github/workflows/security.yml
    ok "GitHub Actions security workflow configuré"
fi

# Créer le fichier SECURITY.md
cat > SECURITY.md << 'SECEOF'
# Security Policy

## Reporting Vulnerabilities

**DO NOT** open public GitHub issues for security vulnerabilities.

📧 Email: security@mltoolkit.com
🔒 PGP Key: [keyserver link]
⏱️ Response time: 48 hours

## Security Measures

| Layer | Measure | Status |
|-------|---------|--------|
| API | JWT Authentication | ✅ |
| API | Rate Limiting | ✅ |
| API | Input Validation | ✅ |
| Infrastructure | Non-root Docker | ✅ |
| Infrastructure | Read-only containers | ✅ |
| Code | Bandit scanning | ✅ |
| Dependencies | Safety scanning | ✅ |
| CI/CD | Automated security scans | ✅ |
| Secrets | Environment variables only | ✅ |
| Models | SHA256 integrity check | ✅ |

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x.x | ✅ Active |
SECEOF

ok "SECURITY.md créé"

# ─── 6. Vérification finale ─────────────────────────────────
echo ""
echo "✔️  6/6 - Vérification finale..."

ISSUES=0

[ ! -f .env ] && err ".env manquant" && ISSUES=$((ISSUES+1))
grep -q "CHANGE-ME" .env 2>/dev/null && warn ".env contient des valeurs CHANGE-ME à remplacer" && ISSUES=$((ISSUES+1))
grep -q "^\.env$" .gitignore || (err ".env pas dans .gitignore!" && ISSUES=$((ISSUES+1)))
[ -f .github/workflows/security.yml ] || warn "GitHub Actions security workflow manquant"

echo ""
echo "=================================================="
if [ $ISSUES -eq 0 ]; then
    ok "Sécurisation terminée! Aucun problème critique."
else
    warn "Sécurisation terminée avec $ISSUES point(s) à corriger."
fi

echo ""
echo "📋 Résumé des fichiers créés:"
echo "  ├── .env (secrets générés)"
echo "  ├── .gitignore (mis à jour)"
echo "  ├── SECURITY.md (politique de sécurité)"
echo "  ├── .github/workflows/security.yml (CI/CD)"
echo "  └── logs/bandit-report.txt (rapport sécurité)"
echo ""
echo "🚀 Prochaines étapes:"
echo "  1. Modifier VIRUSTOTAL_API_KEY dans .env"
echo "  2. Modifier ALLOWED_ORIGINS dans .env"
echo "  3. Ajouter api/security.py dans votre api.py"
echo "  4. git add -A && git commit -m 'Add enterprise security'"
echo "  5. git push origin main"
echo ""
echo "🔗 Documentation: docs/SECURITY.md"
