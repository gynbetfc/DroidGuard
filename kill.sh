#!/data/data/com.termux/files/usr/bin/bash
# DroidGuard - Mata o bot com Avada Kedavra

echo "💀 AVADA KEDAVRA! Matando o DroidGuard..."

# Escrever a palavra mágica
echo "avadakadabra" > /tmp/droidguard_morrer.txt

# Aguardar o bot se matar
sleep 2

# Forçar morte se necessário
pkill -f droidguard_bot.py 2>/dev/null

# Limpar
rm -f /tmp/droidguard_morrer.txt

echo "✅ DroidGuard morto com sucesso!"
