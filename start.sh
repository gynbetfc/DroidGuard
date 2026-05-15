#!/data/data/com.termux/files/usr/bin/bash
# DroidGuard - Inicializador Persistente
# Roda em background mesmo com o Termux fechado

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🛡️ DROIDGUARD - INICIALIZADOR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Corrigir DNS se necessário
echo "nameserver 8.8.8.8" > /data/data/com.termux/files/usr/etc/resolv.conf 2>/dev/null

# Instalar dependências se necessário
if ! command -v termux-camera-photo &> /dev/null; then
    echo "📦 Instalando termux-api..."
    pkg install -y termux-api termux-tools
fi

if ! python -c "import requests" 2>/dev/null; then
    echo "📦 Instalando requests..."
    pip install requests
fi

# Baixar o bot mais recente
echo "📥 Baixando DroidGuard bot..."
curl -k -s -o /tmp/droidguard_bot.py https://raw.githubusercontent.com/gynbetfc/DroidGuard/main/droidguard_bot.py

# Garantir permissão
chmod +x /tmp/droidguard_bot.py

# Matar instância anterior
pkill -f droidguard_bot.py 2>/dev/null

# Iniciar em background (sobrevive ao fechar Termux)
echo "🚀 Iniciando DroidGuard em background..."
nohup python /tmp/droidguard_bot.py > /tmp/droidguard.log 2>&1 &

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DROIDGUARD RODANDO!"
echo "📱 PID: $!"
echo "💀 Para matar: echo 'avadakadabra' > /tmp/droidguard_morrer.txt"
echo "📝 Logs: cat /tmp/droidguard.log"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
