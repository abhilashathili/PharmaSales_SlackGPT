import joblib
import pandas as pd
from app.helpers.segments import *

model = joblib.load("app/model/hcp_segmentation_model.pkl")
encoder = joblib.load("app/model/hcp_encoder.pkl")
raw_df = pd.read_csv("app/data/xponent_data.csv")

def predict_doctor_segment(doctor_name):
    matches = raw_df[raw_df["Prescriber_Name"].str.lower().str.contains(doctor_name.lower())]
    if matches.empty:
        return f"Sorry, I couldn't find any data for Dr. {doctor_name}."

    matches = matches.copy()
    matches["Region"] = matches["Prescriber_ZIP"].astype(str).map(region_map)
    matches["Is_Competitor"] = matches["Product_Group"].isin(["172", "173"]).astype(int)
    matches["Is_OwnBrand"] = (matches["Product_Group"] == "171").astype(int)

    doc_id = matches["SRA1_IMS_Doctor#"].iloc[0]
    brand_rx_ratio = matches["Is_OwnBrand"].mean()
    row_count = len(matches)
    rx_type_div = matches["RX_Type"].nunique()
    channel_div = matches["Category"].nunique()

    sample_row = matches.iloc[0][["RX_Type", "Product_Group", "Region"]].to_frame().T
    encoded = encoder.transform(sample_row)
    encoded_df = pd.DataFrame(encoded, columns=encoder.get_feature_names_out(["RX_Type", "Product_Group", "Region"]))

    features = pd.DataFrame({
        "Category": [matches["Category"].iloc[0]],
        "Bucket01": [matches["Bucket01"].mean()],
        "Bucket24": [matches["Bucket24"].mean()],
        "Bucket25": [matches["Bucket25"].mean()],
        "BrandRxRatio": [brand_rx_ratio],
        "RowCountPerHCP": [row_count],
        "RX_Type_Diversity": [rx_type_div],
        "ChannelDiversity": [channel_div],
        "Is_Competitor": [matches["Is_Competitor"].mean()],
        "Is_OwnBrand": [matches["Is_OwnBrand"].mean()]
    }).reset_index(drop=True)

    X_input = pd.concat([features, encoded_df.reset_index(drop=True)], axis=1)
    prediction = model.predict(X_input)[0]
    strategy = segment_strategies.get(prediction, "[Strategy not available]")
    
    response = (
    f"Dr. {doctor_name} is classified as a *{prediction}*.\n"
    f"💡 Suggested Strategy: {strategy}"
    )
    return response
