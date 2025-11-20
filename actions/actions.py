from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests

from .collection_mapping import COLLECTION_MAPPING


# ---------------------------------------------------------
# FORMATAGE POUR WHATSAPP CLOUD API (image + caption)
# ---------------------------------------------------------
def format_whatsapp_product(p):
    title = p.get("title", "Nom inconnu")
    price = p.get("price", "Prix non défini")
    description = p.get("description", "")
    image_url = p.get("imageUrl", "")
    variants = p.get("variants", [])

    caption = f"⭐ *{title}*\n💰 {price} FCFA\n"

    if description:
        caption += f"\n📄 *Description* : {description}\n"

    if variants:
        caption += "\n🎨 *Variantes* :\n"
        for v in variants:
            size = v.get("size", "Taille inconnue")
            color = v.get("color", "Couleur inconnue")
            v_price = v.get("price", price)
            stock = v.get("stock", 0)
            caption += f"• {size} | {color} — {v_price} FCFA (Stock : {stock})\n"

    return image_url, caption


# ---------------------------------------------------------
# BASE CLASS POUR ENVOYER LES PRODUITS WHATSAPP
# ---------------------------------------------------------
def send_whatsapp_products(dispatcher, products, intro_text):
    """
    Envoi structuré compatible WhatsApp Cloud API.
    Chaque produit = une réponse indépendante avec image + caption.
    """

    dispatcher.utter_message(text=intro_text)

    for p in products:
        image_url, caption = format_whatsapp_product(p)

        # WhatsApp Cloud API payload structure
        dispatcher.utter_message(
            attachment={
                "type": "image",
                "payload": {"url": image_url}
            },
            text=caption
        )


# ---------------------------------------------------------
# 1. Recherche par nom
# ---------------------------------------------------------
class ActionSearchProductByName(Action):
    def name(self):
        return "action_search_product_by_name"

    def run(self, dispatcher, tracker, domain):
        product_name = tracker.get_slot("product_name")

        if not product_name:
            dispatcher.utter_message(text="Quel produit recherchez-vous ?")
            return []

        url = f"http://localhost:3000/product/search?title={product_name}"

        try:
            res = requests.get(url)
            if res.status_code != 200:
                dispatcher.utter_message(text="Erreur serveur.")
                return []

            products = res.json()
            if not products:
                dispatcher.utter_message(text="Aucun produit trouvé.")
                return []

            send_whatsapp_products(
                dispatcher,
                products,
                f"Voici ce que j’ai trouvé pour *{product_name}* 🔎"
            )

        except Exception as e:
            dispatcher.utter_message(text=f"Erreur : {e}")

        return []


# ---------------------------------------------------------
# 2. Recherche par catégorie
# ---------------------------------------------------------
class ActionSearchProductByCategory(Action):
    def name(self):
        return "action_search_product_by_category"

    def run(self, dispatcher, tracker, domain):
        category = tracker.get_slot("category")

        if not category:
            dispatcher.utter_message(text="Quelle catégorie souhaitez-vous ?")
            return []

        url = f"http://localhost:3000/product/category?name={category}"

        try:
            res = requests.get(url)
            if res.status_code != 200:
                dispatcher.utter_message(text="Erreur serveur.")
                return []

            products = res.json()
            if not products:
                dispatcher.utter_message(text="Aucun produit dans cette catégorie.")
                return []

            send_whatsapp_products(
                dispatcher,
                products,
                f"🗂️ Produits dans la catégorie *{category}* :"
            )

        except Exception as e:
            dispatcher.utter_message(text=f"Erreur : {e}")

        return []


# ---------------------------------------------------------
# 3. Recherche par budget
# ---------------------------------------------------------
class ActionSearchProductByBudget(Action):
    def name(self):
        return "action_search_product_by_budget"

    def run(self, dispatcher, tracker, domain):
        budget = tracker.get_slot("budget")

        if not budget:
            dispatcher.utter_message(text="Quel est votre budget maximum ?")
            return []

        url = f"http://localhost:3000/product/budget?max={budget}"

        try:
            res = requests.get(url)
            if res.status_code != 200:
                dispatcher.utter_message(text="Erreur serveur.")
                return []

            products = res.json()
            if not products:
                dispatcher.utter_message(text=f"Aucun produit sous {budget} FCFA.")
                return []

            send_whatsapp_products(
                dispatcher,
                products,
                f"💵 Produits à moins de {budget} FCFA :"
            )

        except Exception as e:
            dispatcher.utter_message(text=f"Erreur : {e}")

        return []


# ---------------------------------------------------------
# 4. Recherche par collection (occasion)
# ---------------------------------------------------------
class ActionSearchProductByCollection(Action):
    def name(self):
        return "action_search_product_by_collection"

    def run(self, dispatcher, tracker, domain):
        collection = tracker.get_slot("collection")

        if not collection:
            dispatcher.utter_message(text="Pour quelle occasion cherchez-vous ?")
            return []

        mapped = COLLECTION_MAPPING.get(collection.lower())
        if not mapped:
            dispatcher.utter_message(text="Je n'ai pas compris l’occasion.")
            return []

        url = f"http://localhost:3000/product/collection?name={mapped}"

        try:
            res = requests.get(url)
            if res.status_code != 200:
                dispatcher.utter_message(text="Erreur serveur.")
                return []

            products = res.json()
            if not products:
                dispatcher.utter_message(text="Aucun produit dans cette collection.")
                return []

            send_whatsapp_products(
                dispatcher,
                products,
                f"🎉 Suggestions pour *{collection}* :"
            )

        except Exception as e:
            dispatcher.utter_message(text=f"Erreur : {e}")

        return []
