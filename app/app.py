import pandas as pd
import os, re
from app.helpers.strings import *
from slack_bolt import App
from dotenv import load_dotenv
load_dotenv()
from app.handlers import *

app = App(token=os.getenv("SLACK_BOT_TOKEN"))

user_context = {}

@app.event("app_mention")
def slack_events(body, say, logger):
    text = body.get("event", {}).get("text", "")
    user = body.get("event", {}).get("user", "")
    drug,doctor_name = None, None

    if re.search(r"\b(hi|hello|help)\b", text.lower()):
        say(welcome_message)
        return

    intent = classify_intent(text)
    print(intent)
    
    # Medical Query
    if intent == "medical_query":
        drug = extract_drug_names(text,drug_list) or user_context.get(user, {}).get("last_drug")

        # Memory fallback
        if not drug and re.search(r"\b(it|its)\b", text.lower()):
            drug = user_context.get(user, {}).get("last_drug")

        response = drug_info(text,drug)
        say(response)

    # HCP Query
    elif intent == "doctor_info":
        doctor_name = extract_prescriber_name(text)
        if not doctor_name:
            say("I couldn't identify a doctor name in your message. \nTry something like 'Tell me about Dr. Jane Doe.'")
            return
        response = predict_doctor_segment(doctor_name)
        say(response)

    # Unclear Query
    elif intent == "unknown":
        last = user_context.get(user, {})
        if last.get("last_intent") == "medical_query" and last.get("last_drug"):
            say(f"Following up on {last['last_drug']}...")
        drug = last.get("last_drug")
        response = drug_info(text,drug)
        say (response)
    
    else:
        say(unsure)
    
    # Memory Management
    user_context[user] = {
        "last_intent": intent,
        "last_drug": drug or user_context.get(user, {}).get("last_drug"),
    }