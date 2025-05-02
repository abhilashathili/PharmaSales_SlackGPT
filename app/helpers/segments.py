
# Region mapping
region_map = {
    "10001": "Northeast",
    "60601": "Midwest",
    "90001": "West",
    "77001": "South",
    "30301": "South",
    "19103": "Northeast",
    "98101": "West"
}

segment_strategies = {
    "High-Volume Loyalist": (
        "Thanks for checking in. Here's a compliant suggestion for engagement:\n"
        "• Continue consistent, educational engagement using MLR-approved materials.\n"
        "• Offer co-branded resources or practice-specific education if available.\n"
        "• Maintain alignment with the HCP’s current practice patterns."
    ),

    "Low-Volume Prescriber": (
        "Here’s how you might approach this HCP:\n"
        "• Share FDA-approved product and clinical use info.\n"
        "• Highlight coverage tools or access support, if applicable.\n"
        "• Offer follow-up through your medical or access team."
    ),

    "New Adopter": (
        "Suggested next steps:\n"
        "• Reinforce prescribing with dosing and efficacy info from the PI.\n"
        "• Provide any starter kits or affordability materials your team has.\n"
        "• Support with additional education as needed."
    ),

    "Aware Non-Prescriber": (
        "Suggested compliant approach:\n"
        "• Share disease education and safety info using approved resources.\n"
        "• Clarify on-label use and help address open questions.\n"
        "• Follow up with medical or clinical education support."
    ),

    "Unaware": (
        "Here’s a compliant approach to raising awareness:\n"
        "• Begin with non-branded disease education.\n"
        "• Introduce the product within its approved indication.\n"
        "• Invite discussion or questions for your medical team."
    ),

    "Managed Care Restricted": (
        "Here’s how you can support the HCP:\n"
        "• Provide access tools like PA forms, coverage guides, or affordability support.\n"
        "• Share compliant coverage info as applicable to their region.\n"
        "• Offer to follow up on reimbursement details with access teams."
    ),

    "Competitor Loyalist": (
        "Here’s a compliant way to position your product:\n"
        "• Focus only on your product’s approved indication and data.\n"
        "• Provide PI and any comparative info approved by MLR.\n"
        "• Avoid direct comparisons unless using reviewed resources."
    )
}
