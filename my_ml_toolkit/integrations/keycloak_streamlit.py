"""
Keycloak Authentication pour Streamlit
Login page avec MFA (TOTP - Google Authenticator compatible)
"""

import os
from dotenv import load_dotenv
load_dotenv()
import httpx
import streamlit as st
from typing import Optional

KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://localhost:8180")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "ml-toolkit")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "ml-streamlit")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_STREAMLIT_SECRET", "")

TOKEN_URL = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
USERINFO_URL = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/userinfo"
LOGOUT_URL = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/logout"


def get_token(username: str, password: str, totp: Optional[str] = None) -> dict:
    """
    Obtenir un token Keycloak avec username/password + MFA optionnel
    """
    data = {
        "client_id": KEYCLOAK_CLIENT_ID,
        "client_secret": KEYCLOAK_CLIENT_SECRET,
        "grant_type": "password",
        "username": username,
        "password": password,
        "scope": "openid profile email",
    }
    
    # Ajouter le code TOTP si fourni
    if totp:
        data["totp"] = totp
    
    try:
        response = httpx.post(TOKEN_URL, data=data, timeout=10)
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        
        error = response.json()
        error_desc = error.get("error_description", "Authentication failed")
        
        # Détecter si MFA requis
        if "totp" in error_desc.lower() or "otp" in error_desc.lower():
            return {"success": False, "mfa_required": True, "error": error_desc}
        
        return {"success": False, "mfa_required": False, "error": error_desc}
        
    except httpx.ConnectError:
        return {"success": False, "error": "Cannot connect to authentication server"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_userinfo(access_token: str) -> dict:
    """Récupérer les infos utilisateur depuis Keycloak"""
    try:
        response = httpx.get(
            USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return {}
    except Exception:
        return {}


def logout():
    """Déconnexion complète"""
    if "refresh_token" in st.session_state:
        try:
            httpx.post(LOGOUT_URL, data={
                "client_id": KEYCLOAK_CLIENT_ID,
                "client_secret": KEYCLOAK_CLIENT_SECRET,
                "refresh_token": st.session_state.refresh_token
            }, timeout=5)
        except Exception:
            pass
    
    # Nettoyer la session
    for key in ["access_token", "refresh_token", "user_info", "authenticated"]:
        st.session_state.pop(key, None)
    
    st.rerun()


def show_login_page():
    """Afficher la page de login avec MFA"""
    
    st.set_page_config(
        page_title="ML Toolkit - Login",
        page_icon="🛡️",
        layout="centered"
    )
    
    # Style CSS
    st.markdown("""
    <style>
        .main { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); }
        .login-box {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 40px;
            backdrop-filter: blur(10px);
        }
        .stButton > button {
            width: 100%;
            background: linear-gradient(90deg, #e94560, #0f3460);
            color: white;
            border: none;
            padding: 12px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("# 🛡️ ML Toolkit")
        st.markdown("#### Malware Detection Platform")
        st.markdown("---")
        
        # Étape 1 : Login standard
        if not st.session_state.get("mfa_pending"):
            
            st.markdown("### 🔐 Sign In")
            
            username = st.text_input(
                "Username",
                placeholder="your.username",
                key="login_username"
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="••••••••",
                key="login_password"
            )
            
            if st.button("Sign In →", use_container_width=True):
                if not username or not password:
                    st.error("Please enter username and password")
                else:
                    with st.spinner("Authenticating..."):
                        result = get_token(username, password)
                    
                    if result["success"]:
                        # Login sans MFA réussi
                        st.session_state.access_token = result["data"]["access_token"]
                        st.session_state.refresh_token = result["data"].get("refresh_token")
                        st.session_state.user_info = get_userinfo(result["data"]["access_token"])
                        st.session_state.authenticated = True
                        st.rerun()
                    
                    elif result.get("mfa_required"):
                        # MFA requis - passer à l'étape 2
                        st.session_state.mfa_pending = True
                        st.session_state.pending_username = username
                        st.session_state.pending_password = password
                        st.rerun()
                    
                    else:
                        st.error(f"❌ {result.get('error', 'Login failed')}")
            
            st.markdown("---")
            st.markdown(
                "<small>🔒 Protected by Keycloak Enterprise SSO</small>",
                unsafe_allow_html=True
            )
        
        # Étape 2 : MFA TOTP
        else:
            st.markdown("### 📱 Two-Factor Authentication")
            st.info(
                "Open your authenticator app "
                "(Google Authenticator, Authy, etc.) "
                "and enter the 6-digit code."
            )
            
            totp_code = st.text_input(
                "Authentication Code",
                placeholder="000000",
                max_chars=6,
                key="totp_input"
            )
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("← Back", use_container_width=True):
                    st.session_state.mfa_pending = False
                    st.rerun()
            
            with col_b:
                if st.button("Verify ✓", use_container_width=True):
                    if len(totp_code) != 6 or not totp_code.isdigit():
                        st.error("Please enter a valid 6-digit code")
                    else:
                        with st.spinner("Verifying..."):
                            result = get_token(
                                st.session_state.pending_username,
                                st.session_state.pending_password,
                                totp=totp_code
                            )
                        
                        if result["success"]:
                            # MFA réussi !
                            st.session_state.access_token = result["data"]["access_token"]
                            st.session_state.refresh_token = result["data"].get("refresh_token")
                            st.session_state.user_info = get_userinfo(result["data"]["access_token"])
                            st.session_state.authenticated = True
                            st.session_state.mfa_pending = False
                            st.success("✅ Authentication successful!")
                            st.rerun()
                        else:
                            st.error(f"❌ Invalid code: {result.get('error', 'Verification failed')}")


def require_auth(func):
    """
    Décorateur pour protéger les pages Streamlit
    
    Usage:
        @require_auth
        def main():
            st.write("Protected content")
    """
    def wrapper(*args, **kwargs):
        if not st.session_state.get("authenticated"):
            show_login_page()
            st.stop()
        return func(*args, **kwargs)
    return wrapper
