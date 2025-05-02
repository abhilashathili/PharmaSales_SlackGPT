import re

def extract_prescriber_name(sentence):
    """
    Extracts a potential prescriber name from a sentence.

    Args:
        sentence: The input sentence string.

    Returns:
        The extracted name string, or None if no likely name is found.
    """

    pattern = r"(?:Dr\.?|dr\.?|DR\.?|Mr\.?|Mrs\.?|Ms\.?)?\s*([A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)+)"
    match = re.search(pattern, sentence)

    if match:
        return match.group(1)
    else:
        return None
    
def extract_drug_names(sentence, drug_list):
    """
    Extracts known drug names from a sentence.

    Args:
        sentence: The input sentence string.
        drug_list: A list of known drug names.

    Returns:
        A list of drug names found in the sentence.
    """
    found_drugs = []
    for drug in drug_list:
        #  Escape any special regex characters in the drug name
        escaped_drug = re.escape(drug)
        if re.search(r"\b" + escaped_drug + r"\b", sentence, re.IGNORECASE):
            found_drugs.append(drug)
    
    return found_drugs[0] if found_drugs else None #just considering the first drug found
