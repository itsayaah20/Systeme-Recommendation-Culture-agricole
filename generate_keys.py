from py_vapid import Vapid

# Initialise Vapid
vapid = Vapid()

# Génère les clés (sans subject ici)
vapid.generate_keys()

# Récupère les clés
public_key = vapid.public_key
private_key = vapid.private_key

print("VAPID_PUBLIC_KEY =", public_key)
print("VAPID_PRIVATE_KEY =", private_key)

# Claims VAPID requis pour la notification web push
claims = {"sub": "mailto:loca.space.08@gmail.com"}
print("VAPID_CLAIMS =", claims)
