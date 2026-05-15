#!/data/data/com.termux/files/usr/bin/bash
# Verifica se o DroidGuard está rodando

if pgrep -f "droidguard_bot.py" > /dev/null; then
    PID=$(pgrep -f droidguard_bot.py)
    echo "✅ DroidGuard está RODANDO"
    echo "📱 PID: $PID"
    echo "💀 Para matar: ./kill.sh"
else
    echo "❌ DroidGuard está PARADO"
    echo "🚀 Para iniciar: ./start.sh"
fi
