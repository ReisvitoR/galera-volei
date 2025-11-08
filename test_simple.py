"""
Teste simples dos endpoints de convites usando uv run
"""
import subprocess
import json
import time

def run_request(method, url, data=None, headers=None):
    """Executa uma requisição HTTP usando uv"""
    cmd = ['uv', 'run', 'python', '-c']
    
    python_code = f'''
import requests
import json

try:
    '''
    
    if method.upper() == 'GET':
        python_code += f'''
    response = requests.get("{url}"'''
        if headers:
            python_code += f''', headers={headers}'''
        python_code += ''')
    '''
    elif method.upper() == 'POST':
        python_code += f'''
    response = requests.post("{url}"'''
        if data:
            python_code += f''', json={data}'''
        if headers:
            python_code += f''', headers={headers}'''
        python_code += ''')
    '''
    
    python_code += '''
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {response.json()}")
    except:
        print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
'''
    
    cmd.append(python_code)
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=r"c:\Users\Nazir Reis\Documents\galera-volei")
    return result.stdout, result.stderr

def test_api():
    print("🚀 Testando API do sistema de convites\n")
    
    # Teste 1: Health check
    print("1️⃣ Testando health check...")
    stdout, stderr = run_request('GET', 'http://127.0.0.1:8000/health')
    print(f"   Output: {stdout}")
    if stderr:
        print(f"   Error: {stderr}")
    
    # Teste 2: Verificar documentação
    print("\n2️⃣ Testando documentação...")
    stdout, stderr = run_request('GET', 'http://127.0.0.1:8000/docs')
    print(f"   Output: {stdout}")
    
    # Teste 3: Registrar usuário
    print("\n3️⃣ Registrando usuário teste...")
    user_data = {
        "nome": "Teste Convites",
        "email": "teste.convites@email.com", 
        "senha": "123456"
    }
    stdout, stderr = run_request('POST', 'http://127.0.0.1:8000/api/v1/auth/register', data=user_data)
    print(f"   Output: {stdout}")
    
    time.sleep(1)
    
    print("\n✅ Testes básicos concluídos!")
    print("\n📖 Para testar completamente o sistema de convites:")
    print("   1. Acesse http://127.0.0.1:8000/docs")
    print("   2. Registre dois usuários")
    print("   3. Faça login com cada um")
    print("   4. Crie uma partida privada com um usuário")
    print("   5. Envie um convite para o outro usuário")
    print("   6. Aceite o convite")

if __name__ == "__main__":
    test_api()