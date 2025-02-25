import requests
import time
import os

# Configurações
GROUP_ID = 34812705  # Substitua pelo ID do seu grupo
COOKIE = "070CFDC2D0FAFADBD9F9452CBA3E88321138E9D046661F081AAD844AA8A9F42F8817332450A827EAB0BEE113B388665A672BA38AFBFCCADFF3C2F8379E8C0A720B927F11D5705DFB6E42C3EA4C635AE4A8A4FFA78C6A48BFCCCF2167C516393921F8346BCA483DCA49E6E85612C53FD917FDE94CCBB085F2267F5BC650C582E08B2186BFD1DA6969E37927604EBF131FAE5F54E0339044AB0A4DC054E072A69CF62BA67B3DE6EB1AAEE9CE66B4D5C0E602D6F16A658EDEEF1D04D58B54052D1F31940167A4642B02A3AEA1E956FE956FB17248AC6170C9A1E52796D38C11C3DC8DC9D024289C86C82B173B8D3BD304E755C86D3A96A6125ED379E6FD9B483490FDEBD42ED37D7CFB64FD8C1A5065FBE70A4CAC2DE142C533AADBB02D2F80869614811B6B3B31CA6AAF174D7C687527CB8F924465DAE5EB9CE22A4392AEA398F4FC6422D3F846C3C36092108C80C086CDCF5AADDC42C0D072F7895DD9DAA73FF35EDADD090206C354586B0EDCF87B6A86DFE74B53E1D3520936CB4D09A00F4E829292A6E3BC29AF95DF838623100C69A73C32905E460F8CB0587769C43BA399CDE49B7C9C3C9C7FD741C8F32251C562CB81E46F5CCE891AD54F078FA0470B6B942D65E02C79F1688F7E04DAC3AAD19BFB251D1E44395198B92174E731DB9216765AFDF2ED74F8D1F9B556FAF080E183CA08D9B1E2FBD5AF2BA15501E6F667E3852193CA715957B2F0DEC1BCD4F1FC22C1B5C30A7D2744AF39D72B7F633EC02BE49067E0EC858FD42D9E55D45EE6D513A6A1ED9600ADE97578019462C899FB6BF5C568714E23119DF23A766D117E25FB0B6986D8BB52AF5B01B3CD77BED3077FBE0CFEDF455C6320712BFBA85550E72F54F4383613C6A17BB12A6A9D72B37747021A165770D5AE02029CAF6952C3C2D2E644C60E225116B64E09DABA22A87C7C6A5EC2499C559FB3433D37C278099D3118C9AE07F2707D429AB60C4AFBB7E312CC1EA062CC11F715343D7E7EBB0279C036617A6082EEE72DD1393AF6CDC496A149E2F1EC6E3C9D9D694074C4497D5D27BCCA0FD0B2F7194E57126F1FE7968583BFBBB4F1A4923007A71FFE3251B701029372AD3AEE0A6EDFCDF35B407B9E694A6C17F05A9D"  # 🔹 Substitua pelo seu 
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1336429788016939171/h1rNRRJFJVfYwnJdKXZaDLx9xW9ka8oo1UsOVK0c_BjX7cZyn3PBJFrblF_hXwBR9rd2"  # 🔹 Substitua pela URL do webhook
EXPULSAR_APOS = 5  # Número de mudanças antes da expulsão

HEADERS = {
    "Cookie": f".ROBLOSECURITY={COOKIE}",
    "Content-Type": "application/json",
    "User-Agent": "RobloxBot"
}

old_roles = {}  # Guarda os cargos anteriores dos usuários
modifications = {}  # Guarda quantas vezes cada usuário alterou cargos

def send_discord_alert(admin_id, admin_name, changed_users, expelled):
    """ Envia um alerta para o Discord sobre mudanças suspeitas. """
    status = "✅ Expulso do grupo" if expelled else "❌ Não expulso"
    changed_list = "\n".join([f"- [{uid}](https://www.roblox.com/users/{uid}/profile)" for uid in changed_users])

    data = {
        "username": "Alerta de Raid",
        "embeds": [{
            "title": "⚠️ Tentativa de RAID Detectada!",
            "description": f"**Admin:** [{admin_name}](https://www.roblox.com/users/{admin_id}/profile)\n"
                           f"**Mudou cargos de {len(changed_users)} jogadores**:\n{changed_list}\n\n"
                           f"**Status:** {status}",
            "color": 16711680  # Vermelho
        }]
    }
    requests.post(DISCORD_WEBHOOK_URL, json=data)

def get_username(user_id):
    """ Obtém o nome de usuário de um ID do Roblox. """
    url = f"https://users.roblox.com/v1/users/{user_id}"
    response = requests.get(url, headers=HEADERS)
    return response.json().get("name", "Desconhecido") if response.status_code == 200 else "Erro"

def expel_user(user_id):
    """ Expulsa um usuário do grupo. """
    url = f"https://groups.roblox.com/v1/groups/{GROUP_ID}/users/{user_id}"
    response = requests.delete(url, headers=HEADERS, json={"reason": "Tentativa de raid"})
    return response.status_code == 200  # Retorna True se a expulsão funcionou

def get_group_roles():
    """ Obtém os cargos do grupo. """
    url = f"https://groups.roblox.com/v1/groups/{GROUP_ID}/roles"
    response = requests.get(url, headers=HEADERS)
    return response.json().get("roles", []) if response.status_code == 200 else []

def get_group_members(role_id):
    """ Obtém os membros de um cargo. """
    url = f"https://groups.roblox.com/v1/groups/{GROUP_ID}/roles/{role_id}/users"
    response = requests.get(url, headers=HEADERS)
    return [user["userId"] for user in response.json().get("data", [])] if response.status_code == 200 else []

def track_role_changes():
    """ Monitora mudanças de cargo. """
    global old_roles
    print("✅ Script iniciado. Monitorando mudanças de cargo...")

    while True:
        new_roles = {}
        changes = {}

        # Obtém todos os cargos do grupo
        for role in get_group_roles():
            role_id = role["id"]
            members = get_group_members(role_id)
            for member in members:
                new_roles[member] = role_id

        # Detecta mudanças de cargo
        for user_id, role_id in new_roles.items():
            if user_id in old_roles and old_roles[user_id] != role_id:
                changes[user_id] = old_roles[user_id]  # Guarda o cargo antigo

        if changes:
            print(f"⚠️ Mudanças detectadas: {changes}")

            # Verifica quem fez as mudanças
            admin_changes = {}
            for user, old_role in changes.items():
                admin_id = new_roles.get(user)  # Supondo que o último cargo seja o responsável
                if admin_id:
                    if admin_id not in admin_changes:
                        admin_changes[admin_id] = []
                    admin_changes[admin_id].append(user)

            for admin_id, changed_users in admin_changes.items():
                if admin_id not in modifications:
                    modifications[admin_id] = 0
                modifications[admin_id] += len(changed_users)

                admin_name = get_username(admin_id)
                expelled = False

                # Se atingiu o limite, expulsa
                if modifications[admin_id] >= EXPULSAR_APOS:
                    expelled = expel_user(admin_id)

                # Envia alerta no Discord
                send_discord_alert(admin_id, admin_name, changed_users, expelled)

        old_roles = new_roles.copy()
        time.sleep(10)  # Verifica a cada 10 segundos

# Iniciar monitoramento
track_role_changes()
