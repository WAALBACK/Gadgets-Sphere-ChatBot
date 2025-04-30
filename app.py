import json
import random
from flask import Flask, request, jsonify, render_template
import pyttsx3
import speech_recognition as sr
import spacy

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '').lower()
    print("User input:", user_input)

    doc = nlp(user_input)
    entities = [ent.text.lower() for ent in doc.ents]
    print("Entities detected:", entities)

    if any(word in user_input for word in ["list", "available", "show all"]):
        response = "Here are the available gadgets and accessories:\n"
        for category, items in gadgets_data.items():
            response += f"\n{category.title()}:\n"
            for item in items:
                response += f"- {item['name']} by {item['brand']}\n"
        return jsonify({'response': response})

    for category in gadgets_data.values():
        for item in category:
            if item['name'].lower() in user_input or item['name'].lower() in entities:
                if any(kw in user_input for kw in ["detail", "spec", "information", "about"]):
                    response = f"{item['name']} Specs:\n{item['specs']}\nStorage Options: {', '.join(item['storage'])}\nPrice: {item['price']}"
                    return jsonify({'response': response})

                if "advantage" in user_input or "disadvantage" in user_input:
                    adv = "\n".join(f"- {a}" for a in item['advantages'])
                    disadv = "\n".join(f"- {d}" for d in item['disadvantages'])
                    return jsonify({'response': f"Advantages:\n{adv}\nDisadvantages:\n{disadv}"})

                if "negotiate" in user_input or "discount" in user_input:
                    original = item['price']
                    discounted = f"${int(item['price'].strip('$')) - random.randint(20, 100)}"
                    return jsonify({'response': f"Original: {original}\nSpecial Offer: {discounted}"})

    return jsonify({'response': "I can help with gadget info, prices, and specs. Try asking for 'details of iPhone 14' or 'advantages of Galaxy S23'."})

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
    app.run(debug=True)
