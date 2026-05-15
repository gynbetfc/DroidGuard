#!/data/data/com.termux/files/usr/bin/bash
echo "Instalando DroidGuard..."
pkg update -y
pkg install -y python termux-api termux-tools
pip install requests
curl -k -s -o ~/droidguard_bot.py https://raw.githubusercontent.com/gynbetfc/DroidGuard/main/droidguard_bot.py
chmod +x ~/droidguard_bot.py
echo "✅ Instalado! Execute: python ~/droidguard_bot.py"
