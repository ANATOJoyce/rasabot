const express = require("express");
const axios = require("axios");
const bodyParser = require("body-parser");

const app = express();
app.use(bodyParser.json());

// --------------------------------------
// CONFIGURATION META WHATSAPP
// --------------------------------------
const WHATSAPP_TOKEN = "TON_TOKEN_META";
const PHONE_NUMBER_ID = "TON_PHONE_NUMBER_ID";
const VERIFY_TOKEN = "meta_validation"; // tu peux changer si tu veux

// --------------------------------------
// WEBHOOK RECEPTION : WhatsApp → Rasa
// --------------------------------------
app.post("/webhook", async (req, res) => {
    try {
        const message = req.body.entry?.[0]?.changes?.[0]?.value?.messages?.[0];
        if (!message) return res.sendStatus(200);

        const from = message.from;
        const userMessage = message.text?.body || "";

        console.log("🔵 Message reçu:", userMessage);

        // ENVOI À RASA
        const rasaResponse = await axios.post(
            "http://localhost:5005/webhooks/rest/webhook",
            { sender: from, message: userMessage }
        );

        // REPONSES RASA → WhatsApp
        for (let msg of rasaResponse.data) {

            // Cas 1 : envoi d'une image
            if (msg.attachment && msg.attachment.type === "image") {
                await axios.post(
                    `https://graph.facebook.com/v19.0/${PHONE_NUMBER_ID}/messages`,
                    {
                        messaging_product: "whatsapp",
                        to: from,
                        type: "image",
                        image: { link: msg.attachment.payload.url }
                    },
                    {
                        headers: {
                            Authorization: `Bearer ${WHATSAPP_TOKEN}`,
                            "Content-Type": "application/json"
                        }
                    }
                );
            }

            // Cas 2 : texte
            if (msg.text) {
                await axios.post(
                    `https://graph.facebook.com/v19.0/${PHONE_NUMBER_ID}/messages`,
                    {
                        messaging_product: "whatsapp",
                        to: from,
                        text: { body: msg.text }
                    },
                    {
                        headers: {
                            Authorization: `Bearer ${WHATSAPP_TOKEN}`,
                            "Content-Type": "application/json"
                        }
                    }
                );
            }
        }

        return res.sendStatus(200);

    } catch (err) {
        console.error("❌ ERREUR:", err);
        return res.sendStatus(500);
    }
});

// --------------------------------------
// WEBHOOK VERIFICATION META (GET)
// --------------------------------------
app.get("/webhook", (req, res) => {
    const mode = req.query["hub.mode"];
    const token = req.query["hub.verify_token"];
    const challenge = req.query["hub.challenge"];

    if (mode === "subscribe" && token === VERIFY_TOKEN) {
        console.log(" Webhook validé par Meta !");
        return res.status(200).send(challenge);
    }
    res.sendStatus(403);
});

// --------------------------------------
app.listen(3001, () => {
    console.log(" WhatsApp webhook running on port 3001");
});
