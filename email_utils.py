import random
from django.core.cache import cache
from django.core.mail import send_mail

def generate_verification_code():
    return str(random.randint(100000, 999999))

def send_verification_email(email, code):
    subject = "Votre code de vérification"
    message = f"Bonjour,\n\nVoici votre code de vérification : {code}\n\nCe code est valable 10 minutes."
    from_email = "loca.space.08@gmail.com"  # remplace par ton email expéditeur
    recipient_list = [email]

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
