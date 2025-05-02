import os,difflib, re
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_openai(query, context_chunks):
    context_text = "\n\n".join(context_chunks) if context_chunks else ""
    system_prompt = (
        "You are a medical assistant that answers questions strictly based on the provided knowledge below.\n"
        "If the answer cannot be found in the knowledge, respond with 'I couldn't find that information in the official product resources.'\n"
        "Do not make up anything outside this context.\n\n"
        f"Knowledge:\n{context_text}"
    )

    chat_completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
    )
    print("A GPT-4 prompt has been sent for information retrieval of the drug")
    return chat_completion.choices[0].message.content.strip()

stopwords = {"the", "a", "an", "of", "in", "to", "for", "is", "with", "by", "and", "on", "at", "from"}

# Common synonyms
synonym_map = {
    "makes": "manufactures",
    "produces": "manufactures",
    "maker": "manufacturer",
    "developed": "manufactured",
    "distributes": "distribution",
    "distributed": "distribution",
    "side effect": "side effects",
    "adverse reactions": "side effects",
    "effects": "side effects",
    "uses": "indications",
    "use": "indications",
    "how does": "mechanism",
    "how it works": "mechanism",
    "works": "mechanism"
}

def normalize_query(text):
    text = text.lower()
    for key, val in synonym_map.items():
        text = text.replace(key, val)
    return text

def tokenize(text):
    words = re.findall(r"\b\w+\b", text.lower())
    return set(w for w in words if w not in stopwords)

def load_knowledge_base(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_text(text)

    important_keywords = [
        "hypertension", "blood pressure", "indications", "dosage",
        "administration", "side effects", "warnings", "contraindications",
        "tablet", "extended-release", "treatment", "mg",
        "use", "recommend", "dose", "safety", "effect",
        "prescribing", "healthcare", "doctor", "mechanism", "works",
        "insulin", "glucose", "asthma", "manufacturer", "distribution"
    ]

    filtered_chunks = [
        chunk for chunk in chunks
        if any(keyword in chunk.lower() for keyword in important_keywords)
        and len(chunk) > 100
    ]

    print(f"📦 Loaded {len(filtered_chunks)} relevant chunks (filtered from {len(chunks)} total)")
    print("Sample filtered chunks:")
    for i, chunk in enumerate(filtered_chunks[:3]):
        print(f"\nChunk {i+1}:\n{chunk[:200]}...")
    
    return filtered_chunks

def chunk_text(text, max_length=1000):
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if any(skip in para.lower() for skip in ["cookie", "privacy", "terms", "accessibility", "contact", "copyright"]):
            continue
        if len(para.strip()) < 40:
            continue

        if len(current_chunk) + len(para) < max_length:
            current_chunk += para + "\n\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def search_chunks(query, chunks, threshold=0.09, top_k=2):
    query = normalize_query(query)
    query_keywords = tokenize(query)
    scored_chunks = []

    for chunk in chunks:
        chunk_keywords = tokenize(chunk)
        basic_score = difflib.SequenceMatcher(None, query, chunk.lower()).ratio()
        keyword_score = len(query_keywords & chunk_keywords) / max(len(query_keywords), 1)
        combined_score = (basic_score * 0.3) + (keyword_score * 0.7)

        # FAQs
        chunk_lower = chunk.lower()
        if "side effects" in chunk_lower and "side effects" in query:
            combined_score += 0.1
        elif "mechanism of action" in chunk_lower and "mechanism" in query:
            combined_score += 0.05
        elif "contraindications" in chunk_lower and "contraindications" in query:
            combined_score += 0.05
        elif "warnings" in chunk_lower and "warnings" in query:
            combined_score += 0.03

        scored_chunks.append((combined_score, chunk))

    scored_chunks.sort(reverse=True)

    best_chunks = [chunk for score, chunk in scored_chunks[:top_k] if score >= threshold]

    if best_chunks:
        print(f"🔍 Best match score: {scored_chunks[0][0]:.2f}")
        print("📄 Best chunk preview:\n", best_chunks[0][:300])
        return best_chunks if len(best_chunks) > 1 else best_chunks[0]

    print("⚠️ No chunk passed the threshold.")
    return None

def drug_info(text, drug):

        filepath = f"app/knowledge/{drug.lower().replace(' ', '_')}.txt"
        try:
            knowledge_chunks = load_knowledge_base(filepath)
        except FileNotFoundError:
            return"Sorry, I couldn't find official resources for {drug}."

        chunks = search_chunks(text, knowledge_chunks)
        if isinstance(chunks, list):
            chunks = chunks[0]

        response = ask_openai(text, chunks)
        return response