import requests
from rasa_sdk import Action
from rasa_sdk.events import SlotSet

class ActionSearchProductName(Action):
    def name(self):
        return "action_search_products"

    def run(self, dispatcher, tracker, domain):
        # Récupérer le nom du produit recherché depuis l'entité 'product_name'
        product_name = next(tracker.get_latest_entity_values("product_name"), None)        
        # Vérifier si le nom du produit est vide
        if not product_name:
            dispatcher.utter_message(text="Je n'ai pas compris quel produit vous cherchez. Pouvez-vous préciser ?")
            return []

        # Construire l'URL pour interroger l'API avec le nom du produit
        url = f"http://localhost:3000/product/search?title={product_name}"
        
        try:
            # Faire la requête à l'API
            response = requests.get(url)
            
            # Vérifier si la réponse est réussie (code 200)
            if response.status_code == 200:
                products = response.json()
                if products:
                    # Si des produits sont trouvés, préparer une réponse avec les informations des produits
                    for p in products:
                        product_id = p.get("_id", "0")  # Extraire l'ID du produit
                        product_title = p.get("title", "Produit inconnu")
                        product_description = p.get("description", "Pas de description")
                        product_price = p.get("price", "Non disponible")
                        product_image = p.get("imageUrl", None)  # L'URL de l'image du produit
                        product_variants = p.get("variants", [])
                        
                        variant_info = []
                        for variant in product_variants:
                            # Vérifier si variant est un dictionnaire avant d'appeler .get()
                            if isinstance(variant, dict):
                                variant_info.append(f"Size: {variant.get('size', 'Non spécifié')}, "
                                                     f"Color: {variant.get('color', 'Non spécifié')}, "
                                                     f"Price: {variant.get('price', 'Non spécifié')}, "
                                                     f"Stock: {variant.get('stock', 'Non spécifié')}")
                            else:
                                # Si variant n'est pas un dictionnaire, l'ajouter comme une chaîne de caractères
                                variant_info.append(str(variant))
                        
                        # Préparer le message de la réponse
                        message = f"**{product_title}**\n"
                        message += f"Description: {product_description}\n"
                        message += f"Price: {product_price} FCFA\n"
                        message += f"Variants: {', '.join(variant_info)}\n"
                        
                        # Si une image est disponible, l'ajouter à la réponse
                        if product_image:
                            self.send_image_response(dispatcher, product_image)
                        
                        # Ajouter le bouton "Ajouter au panier"
                        message += "\nCliquez sur le bouton ci-dessous pour ajouter ce produit au panier."
                        
                        # Envoi du texte et bouton "Ajouter au panier"
                        dispatcher.utter_message(text=message, 
                                                 buttons=[{
                                                     "title": "Ajouter au panier", 
                                                     "payload": f"/add_to_cart{{\"product_id\":\"{product_id}\"}}"
                                                 }])
                    
                else:
                    # Si aucun produit n'est trouvé
                    message = "Désolé, je n'ai trouvé aucun produit correspondant à cette recherche."
                    dispatcher.utter_message(text=message)
            else:
                # Si l'API retourne un autre code d'état
                message = "Je rencontre un problème pour récupérer les produits. Veuillez réessayer plus tard."
                dispatcher.utter_message(text=message)
        except requests.exceptions.RequestException as e:
            # En cas d'erreur de connexion
            message = f"Une erreur est survenue lors de la recherche de produits : {str(e)}"
            dispatcher.utter_message(text=message)

        return []

    def send_image_response(self, dispatcher, image_url):
        """Envoie une image via Telegram."""
        dispatcher.utter_message(
            attachment=image_url
        )
