import asyncio
from googletrans import Translator

async def traduire():
    translator = Translator()
    texte_francais = "Bonjour, comment allez-vous aujourd'hui ?"
    traduction = await translator.translate(texte_francais, src='fr', dest='ar')
    
    print("Texte original (français) :", texte_francais)
    print("Traduction (darija - arabe) :", traduction.text)

asyncio.run(traduire())
