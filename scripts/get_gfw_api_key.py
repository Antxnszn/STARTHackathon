#!/usr/bin/env python3
"""
Script interactivo para obtener una API Key de Global Forest Watch (GFW).
Automatiza el proceso de login/registro y generación de llave.
"""
import getpass
import json
import httpx
import sys
import asyncio

# Colores y estilos
BOLD = "\033[1m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

BASE_URL = "https://data-api.globalforestwatch.org"

def print_banner():
    print(f"\n{BLUE}╔══════════════════════════════════════════════════════════╗")
    print(f"║       GFW API Key Generator                              ║")
    print(f"╚══════════════════════════════════════════════════════════╝{RESET}\n")
    print("Este script te ayudará a obtener tu API Key de Global Forest Watch.")
    print("Nota: Si ya tienes cuenta de GFW creada con Google/Facebook,")
    print("      es mejor crear una nueva con email/password para la API.\n")

async def get_token(email, password):
    """Obtiene el token de acceso usando credenciales"""
    print(f"🔄 Intentando iniciar sesión como {BOLD}{email}{RESET}...")
    async with httpx.AsyncClient() as client:
        try:
            # Login endpoint (x-www-form-urlencoded)
            data = {
                "username": email,
                "password": password
            }
            response = await client.post(
                f"{BASE_URL}/auth/token",
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                print(f"{GREEN}✅ Login exitoso.{RESET}")
                return response.json().get("access_token")
            elif response.status_code == 401:
                return None
            else:
                print(f"{RED}❌ Error en login ({response.status_code}): {response.text}{RESET}")
                return None
        except Exception as e:
            print(f"{RED}❌ Error de conexión: {e}{RESET}")
            return None

async def sign_up(email):
    """Registra un nuevo usuario"""
    print(f"\n{YELLOW}⚠️  No pudimos iniciar sesión.{RESET}")
    choice = input(f"¿Deseas crear una cuenta nueva para {BOLD}{email}{RESET}? (s/n): ").lower()
    
    if choice != 's':
        return False
        
    password = getpass.getpass("Ingresa una contraseña para tu nueva cuenta: ")
    confirm = getpass.getpass("Confirma la contraseña: ")
    
    if password != confirm:
        print(f"{RED}❌ Las contraseñas no coinciden.{RESET}")
        return False
        
    # Nombre opcional, usaremos la parte del email
    name = email.split('@')[0]
        
    print(f"🔄 Registrando cuenta para {email}...")
    async with httpx.AsyncClient() as client:
        try:
            # Minimal payload - GFW API rejected password/application fields
            payload = {
                "email": email
            }
            
            response = await client.post(f"{BASE_URL}/auth/sign-up", json=payload)
            
            if response.status_code in [200, 201]:
                print(f"{GREEN}✅ Solicitud enviada.{RESET}")
                print(f"\n{YELLOW}⚠️  IMPORTANTE: GFW requiere verificar tu email.{RESET}")
                print("1. Revisa tu bandeja de entrada (y spam).")
                print("2. Haz clic en el enlace para establecer tu contraseña.")
                print("3. Una vez tengas tu contraseña, vuelve a ejecutar este script para obtener la API Key.")
                return None
            elif response.status_code == 422:
                 # Try with extras if minimal failed, or debug output
                 print(f"{RED}❌ Error de validación: {response.text}{RESET}")
                 return None
            else:
                print(f"{RED}❌ Falló el registro ({response.status_code}): {response.text}{RESET}")
                return None
        except Exception as e:
            print(f"{RED}❌ Error: {e}{RESET}")
            return None

async def get_api_key(token):
    """Genera o recupera la API Key"""
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        # 1. Listar llaves existentes
        print(f"\n🔄 Buscando API Keys existentes...")
        response = await client.get(f"{BASE_URL}/api-key", headers=headers)
        
        if response.status_code == 200:
            keys = response.json().get("data", [])
            valid_keys = [k for k in keys if not k.get("revoked")] # Filtrar revocadas si aplica
            
            if valid_keys:
                key = valid_keys[0].get("api_key")
                print(f"{GREEN}✅ API Key encontrada.{RESET}")
                return key
                
        # 2. Crear nueva llave si no hay
        print(f"🔄 Generando nueva API Key...")
        payload = {
            "alias": "greenpass_hackathon_key",
            "email": "hackathon@example.com", # Email de contacto para la key
            "organization": "GreenPass",
            "domains": [] # Empty for development/testing
        }
        
        response = await client.post(
            f"{BASE_URL}/api-key", 
            json=payload, 
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            data = response.json().get("data", {})
            return data.get("api_key")
        else:
            print(f"{RED}❌ Error generando key ({response.status_code}): {response.text}{RESET}")
            return None

async def main():
    print_banner()
    
    email = input("Ingresa tu email: ").strip()
    if not email:
        print("El email es requerido.")
        return

    password = getpass.getpass("Ingresa tu contraseña (o contraseña deseada si eres nuevo): ")
    
    # 1. Intentar Login
    token = await get_token(email, password)
    
    # 2. Si falla login, intentar Registro
    if not token:
        token = await sign_up(email)
        
    if not token:
        print(f"\n{RED}❌ No se pudo autenticar. Por favor verifica tus credenciales o regístrate en la web.{RESET}")
        return

    # 3. Obtener API Key
    api_key = await get_api_key(token)
    
    if api_key:
        print(f"\n{GREEN}╔══════════════════════════════════════════════════════════╗")
        print(f"║  TU GFW API KEY:                                         ║")
        print(f"║  {BOLD}{api_key}{RESET}  ║")
        print(f"╚══════════════════════════════════════════════════════════╝{RESET}")
        print("\nCopia esta llave y agrégala a tu archivo .env:")
        print(f"\n{BOLD}GFW_API_KEY={api_key}{RESET}\n")
    else:
        print(f"\n{RED}❌ No se pudo obtener la API Key.{RESET}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nOperación cancelada.")
    except Exception as e:
        print(f"\nError inesperado: {e}")
