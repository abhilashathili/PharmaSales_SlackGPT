import os
# Load drug names from the knowledge directory (e.g., 'Glytora.txt' becomes 'Glytora')
DRUG_KNOWLEDGE_DIR = "app/knowledge"
drug_list = [
    os.path.splitext(f)[0]
    for f in os.listdir(DRUG_KNOWLEDGE_DIR)
    if f.endswith(".txt")
]

print("Drugs with info in the database:", ", ".join(drug_list))