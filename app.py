import json
import random
import os
from flask import Flask, request, jsonify, render_template
import pyttsx3
import speech_recognition as sr
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Sample data - in a real scenario this would come from a database or external API
gadgets_data = {
    "smartphones": [
        {
            "name": "iPhone 14",
            "brand": "Apple",
            "storage": ["128GB", "256GB", "512GB"],
            "price": "$799",
            "specs": "A15 Bionic chip, Dual-camera system, 5G",
            "advantages": ["High performance", "Excellent camera", "Long software support"],
            "disadvantages": ["Expensive", "No headphone jack"]
        },
        {
            "name": "Galaxy S23",
            "brand": "Samsung",
            "storage": ["128GB", "256GB"],
            "price": "$699",
            "specs": "Snapdragon 8 Gen 2, AMOLED Display, Triple-camera",
            "advantages": ["Great display", "High speed", "Expandable storage"],
            "disadvantages": ["Bloatware", "Can overheat"]
        }
    ],
    "laptops": [
        {
            "name": "Dell XPS 13",
            "brand": "Dell",
            "storage": ["256GB", "512GB", "1TB"],
            "price": "$999",
            "specs": "Intel i7, 16GB RAM, 4K display",
            "advantages": ["Compact", "High performance", "Beautiful display"],
            "disadvantages": ["Pricey", "Limited ports"]
        }
    ]
}

def find_gadget(name):
    for category in gadgets_data.values():
        for item in category:
            if item['name'].lower() == name.lower():
                return item
    return None

def get_bot_response(user_input):
    user_input = user_input.lower()

    if "list" in user_input:
        response = "📦 Available gadgets and accessories:\n"
        for category, items in gadgets_data.items():
            response += f"\n{category.title()}:\n"
            for item in items:
                response += f"• {item['name']} ({item['brand']})\n"
        return response

    elif "details" in user_input:
        name = user_input.replace("details of", "").strip()
        item = find_gadget(name)
        if item:
            return (
                f"📱 {item['name']} by {item['brand']}\n"
                f"📮 Storage: {', '.join(item['storage'])}\n"
                f"💵 Price: {item['price']}\n"
                f"📋 Specs: {item['specs']}"
            )
        return "❌ Gadget not found."

    elif "negotiate" in user_input:
        name = user_input.replace("negotiate", "").strip()
        item = find_gadget(name)
        if item:
            original = item['price']
            discounted = f"${int(item['price'].strip('$')) - random.randint(20, 100)}"
            return f"💬 Original Price: {original}\n🏱 Special Offer: {discounted}"
        return "❌ No price info available."

    elif "advantages" in user_input or "disadvantages" in user_input:
        name = (
            user_input.replace("advantages of", "")
                      .replace("disadvantages of", "")
                      .strip()
        )
        item = find_gadget(name)
        if item:
            adv = "\n".join(f"✓ {a}" for a in item['advantages'])
            disadv = "\n".join(f"✘ {d}" for d in item['disadvantages'])
            return f"✅ Advantages:\n{adv}\n\n⚠️ Disadvantages:\n{disadv}"
        return "❌ No info available."

    else:
        return (
            "🤖 I can help with gadget info, specs, and deals.\n"
            "Try: 'List gadgets', 'Details of iPhone 14', or 'Negotiate Galaxy S23'"
        )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '').lower()
    response = get_bot_response(user_input)
    return jsonify({'response': response})

@app.route('/whatsapp', methods=['POST'])
def whatsapp_reply():
    incoming_msg = request.values.get('Body', '').strip()
    resp = MessagingResponse()
    msg = resp.message()

    bot_response = get_bot_response(incoming_msg)
    msg.body(bot_response)
    return str(resp)

# Voice assistant functions
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return "I didn't catch that. Could you repeat?"
        except sr.RequestError:
            return "Speech recognition service unavailable."

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
