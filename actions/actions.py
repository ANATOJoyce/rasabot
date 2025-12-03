from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests

BACKEND_URL = "http://localhost:3000"

# ---------------------------------------------------------
# ACTION : Recherche produit par nom
# ---------------------------------------------------------
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests

BACKEND_URL = "http://localhost:3000"

class ActionSearchProductByName(Action):
    def name(self):
        return "action_search_product_by_name"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        product_name = tracker.get_slot("product_name")
        if not product_name:
            dispatcher.utter_message(text="Quel produit recherchez-vous ?")
            return []

        try:
            res = requests.get(f"{BACKEND_URL}/product/search", params={"title": product_name})
            res.raise_for_status()
            products = res.json()

            if not products:
                dispatcher.utter_message(text="Aucun produit trouvé.")
                return []

            # Envoi chaque produit à Telegram
            for product in products:
                # On prend la première variante si elle existe
                variant = product.get("variants", [{}])[0]
                price = variant.get("price", product.get("price", "Prix non défini"))

                dispatcher.utter_message(
                    response="utter_search_product",
                    title=product.get("title", "Nom inconnu"),
                    price=price,
                    description=product.get("description", ""),
                    image_url=product.get("imageUrl", ""),
                    product_id=product.get("_id")
                )

        except Exception as e:
            dispatcher.utter_message(text=f"Erreur serveur : {e}")

        return []



class ActionShowProductDetail(Action):
    def name(self):
        return "action_show_product_detail"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        # Récupération de l'ID du produit depuis le slot ou le payload
        product_id = tracker.get_slot("product_id")
        if not product_id:
            dispatcher.utter_message(text="Aucun produit sélectionné.")
            return []

        try:
            res = requests.get(f"{BACKEND_URL}/product/{product_id}")
            res.raise_for_status()
            product = res.json()

            # Affichage du produit (texte, image)
            dispatcher.utter_message(
                text=f"*{product.get('title','Nom inconnu')}*\n"
                     f"Prix: {product.get('price','Prix non défini')} FCFA\n"
                     f"{product.get('description','')}",
                image=product.get("imageUrl","")
            )

        except Exception as e:
            dispatcher.utter_message(text=f"Erreur serveur : {e}")

        return []
    
# ---------------------------------------------------------
# ACTION : Recherche produit par catégorie
# ---------------------------------------------------------
class ActionSearchProductByCategory(Action):
    def name(self):
        return "action_search_product_by_category"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        category = tracker.get_slot("category")
        if not category:
            dispatcher.utter_message(text="Quelle catégorie souhaitez-vous ?")
            return []

        try:
            res = requests.get(f"{BACKEND_URL}/product/category", params={"name": category})
            res.raise_for_status()
            products = res.json()

            if not products:
                dispatcher.utter_message(text="Aucun produit trouvé dans cette catégorie.")
                return []

            # Parcours des produits et envoi via Rasa domain
            for product in products:
                dispatcher.utter_message(
                    response="utter_show_product",
                    product_name=product.get("title", "Nom inconnu"),
                    price=product.get("price", "Prix non défini"),
                    description=product.get("description", ""),
                    image_url=product.get("imageUrl", ""),
                    product_id=str(product.get("id") or product.get("_id", ""))
                )

        except Exception as e:
            dispatcher.utter_message(text=f"Erreur serveur : {e}")

        return []


class ActionCheckout(Action):
    def name(self):
        return "action_checkout"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        # Ici tu peux récupérer le panier depuis un slot ou une base
        cart = tracker.get_slot("cart") or []

        if not cart:
            dispatcher.utter_message(text="Votre panier est vide.")
            return []

        # Exemple simple de confirmation
        dispatcher.utter_message(text="Merci ! Votre commande a été enregistrée. 🛒")

        # Tu peux aussi vider le panier si tu veux
        return [{"slot": "cart", "value": []}]



class ActionAddToCart(Action):
    def name(self):
        return "action_add_to_cart"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message("Produit ajouté au panier !")
        return []