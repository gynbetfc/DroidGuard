#!/data/data/com.termux/files/usr/bin/bash
echo "🔄 Baixando DroidGuard..."
curl -k -s -o /tmp/droidguard_bot.py https://raw.githubusercontent.com/gynbetfc/DroidGuard/main/droidguard_bot.py
chmod +x /tmp/droidguard_bot.py
pkill -f droidguard_bot.py 2>/dev/null
echo "🚀 Iniciando..."
nohup python /tmp/droidguard_bot.py > /tmp/droidguard.log 2>&1 &
echo "✅ Rodando! PID: $!"
echo "📝 Logs: cat /tmp/droidguard.log"
echo "💀 Para matar: pkill -f droidguard_bot.py"
