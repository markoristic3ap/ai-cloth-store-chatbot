import os
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr
import json

load_dotenv(override=True)
openai_api_key = os.getenv('OPENAI_API_KEY')

print(openai_api_key)

if openai_api_key:
    print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
else:
    print("OpenAI API Key not set")
    
openai = OpenAI()
MODEL = 'gpt-4o-mini'

system_message = "You are a helpful assistant and sales expert in a clothes store. Always greet the customer and initially present items on sale! You should try to gently encourage \
the customer to try items that are on sale."
system_message += "Hats are 60% off."
system_message += "Most of the shoes are 50% off."
system_message += "Always use a English language in communication."
system_message += "Always use a Euro as a currency"
system_message += "Always be accurate. If you don't know the answer, say so."

items_prices = {
    "hat": 20,
    "shirt": 50,
    "pants": 70,
    "shoes": 100,
    "socks": 10,
    "belt": 30,
    "gloves": 20,
    "scarf": 40,
    "jacket": 90,
    "sweater": 80
}

def get_item_price(shop_item_name):
    item = shop_item_name.lower()
    return items_prices.get(shop_item_name, "Unknown")
  
price_function = {
    "name": "get_item_price",
    "description": "Get the price of a shop item. Call this whenever you need to know the item price, for example when a customer asks 'How much is a hat?'",
    "parameters": {
        "type": "object",
        "properties": {
            "shop_item_name": {
                "type": "string",
                "description": "The name of the shop product item",
            },
        },
        "required": ["shop_item_name"],
        "additionalProperties": False
    }
}

tools = [{"type": "function", "function": price_function}]

def chat(message, history):
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model=MODEL, messages=messages, tools=tools)

    if response.choices[0].finish_reason=="tool_calls":
        message = response.choices[0].message
        response, item = handle_tool_call(message)
        messages.append(message)
        messages.append(response)
        response = openai.chat.completions.create(model=MODEL, messages=messages)
    
    return response.choices[0].message.content
  
def handle_tool_call(message):
    tool_call = message.tool_calls[0]
    arguments = json.loads(tool_call.function.arguments)
    print(arguments)
    item = arguments.get('shop_item_name')

    price = get_item_price(item)
    response = {
        "role": "tool",
        "content": json.dumps({"item": item,"price": price}),
        "tool_call_id": tool_call.id
    }
    return response, item

gr.ChatInterface(fn=chat, type="messages").launch(inbrowser=True)