import re
from app.helpers.druglist import drug_list
from app.handlers.rag import client

def classify_intent(text):
    """
    Classifies the user's intent based on the message using regular expressions.

    Args:
        text: The user's message.

    Returns:
        A string representing the intent ('doctor_info', 'medical_query', or 'unknown').
    """

    # Patterns for doctor_info intent
    doctor_patterns = [
    r"(tell me about|info about|approach|what about|who is)\s+(?:dr\.?|doctor)\s+[A-Za-z\s]+",
    r"prescribing behavior of\s+(?:dr\.?|doctor)\s+[A-Za-z\s]+",
    r"how do i sell\s+(?:to\s+)?(?:dr\.?|doctor)\s+[A-Za-z\s]+",
    r"targeting strategy for\s+(?:dr\.?|doctor)\s+[A-Za-z\s]+",
    r"what to say to\s+(?:dr\.?|doctor)\s+([A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)+)",
    r"what should i say to\s+(?:dr\.?|doctor)\s+([A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)+)", # Explicitly handles "what should I say to"
    r"near\s+(?:dr\.?|doctor)\s+[A-Za-z\s]+",
    r"(where is|location of)\s+(?:dr\.?|doctor)\s+[A-Za-z\s]+",
    r"contact\s+(?:dr\.?|doctor)\s+[A-Za-z\s]+",
    r"(meet|see)\s+with\s+(?:dr\.?|doctor)\s+([A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)+)",
    r"(talk to|speak with|connect with|interact with|visit)\s+(?:dr\.?|doctor)\s+([A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)+)",
    r"about\s+(?:dr\.?|doctor)\s+[A-Za-z\s]+",
    r"HCP\s+info",
    r"doctor\s+details",
    r"(is it worth|should i|worth (approaching|contacting|seeing|visiting))\s+(?:even\s+)?(?:dr\.?|doctor)\s+[A-Za-z\s]+"
]

    for pattern in doctor_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return "doctor_info"

    # Patterns for medical_query intent (using known drug names)
        # Drug-related queries
    drug_patterns = [
        r"\b(side effects?|adverse effects?|risks?|effects?) of\s+(" + "|".join(drug_list) + r")\b", # Added 's?' for possessive
        r"\b(dose|dosage|how to take|when to take)\s+(" + "|".join(drug_list) + r")\b",
        r"\b(safe|safety|contraindications?|cautions?)\s+(" + "|".join(drug_list) + r")\b", # Added 's?' for possessive
        r"\b(interact(ions)?)\s+(" + "|".join(drug_list) + r")\b", # Added (ions)?
        r"\bhow does\s+(" + "|".join(drug_list) + r")\s+work\b",
        r"\bmechanism of action\s+(" + "|".join(drug_list) + r")\b",
        r"\b(" + "|".join(drug_list) + r")\s+(indications?|used for)\b", # Added 's?' for possessive
        r"\b(" + "|".join(drug_list) + r")\b",  #match drug name alone
        r"\b(tell me about|info about|information on|about)\s+(" + "|".join(drug_list) + r")\b", # Added general info
        r"\b(" + "|".join(drug_list) + r")('s)?\s+(side effects?|dosage|safety|interactions?|contraindications?|cautions?|mechanism of action|uses?|info)\b" # Added possessive
    ]

    for pattern in drug_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return "medical_query"
    
    # Fallback Intent classification using GPT
    intent_prompt = (
        "You are a message classifier for a pharma sales assistant. "
        "Label the user's intent as one of:\n"
        "- `doctor_info`: Asking about an HCP, prescribing behavior, targeting strategy, or what to say to a doctor\n"
        "- `medical_query`: Asking about drug usage, dosage, safety, or product knowledge\n"
        "- `unknown`: Anything else\n\n"
        "Only return one of the three labels. Do not explain.\n\n"
        "Examples:\n"
        "1. 'Tell me about Dr. Smith' → doctor_info\n"
        "2. 'What are the side effects of Glytora?' → medical_query\n"
        "3. 'I'm near Dr. Jodi Griffith, what do I say to her?' → doctor_info\n"
        "4. 'How does Cardiovex work?' → medical_query\n"
        "5. 'Hello' → unknown\n\n"
        f"User message: \"{text}\"\nIntent:"
    )


    intent = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You classify queries into intents."},
            {"role": "user", "content": intent_prompt}
        ]
    )
    print(f"GPT-3.5-turbo has been called to find intent in: {text}")
    return intent.choices[0].message.content.strip().lower().split()[0]
