import pandas as pd, joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder

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

# Load full training data
train_df = pd.read_csv("training_data.csv")

train_df["Region"] = train_df["Prescriber_ZIP"].astype(str).map(region_map)
train_df["Is_Competitor"] = train_df["Product_Group"].isin(["172", "173"]).astype(int)
train_df["Is_OwnBrand"] = (train_df["Product_Group"] == "171").astype(int)

# Aggregated HCP-level features
brand_ratio = train_df.groupby("SRA1_IMS_Doctor#")["Is_OwnBrand"].mean().rename("BrandRxRatio")
row_count = train_df.groupby("SRA1_IMS_Doctor#").size().rename("RowCountPerHCP")
rx_type_diversity = train_df.groupby("SRA1_IMS_Doctor#")["RX_Type"].nunique().rename("RX_Type_Diversity")
channel_diversity = train_df.groupby("SRA1_IMS_Doctor#")["Category"].nunique().rename("ChannelDiversity")

# Merge HCP features
train_df = train_df.merge(brand_ratio, on="SRA1_IMS_Doctor#")
train_df = train_df.merge(row_count, on="SRA1_IMS_Doctor#")
train_df = train_df.merge(rx_type_diversity, on="SRA1_IMS_Doctor#")
train_df = train_df.merge(channel_diversity, on="SRA1_IMS_Doctor#")

# Encode categorical variables
encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
encoded_train = encoder.fit_transform(train_df[["RX_Type", "Product_Group", "Region"]])
encoded_train_df = pd.DataFrame(encoded_train, columns=encoder.get_feature_names_out(["RX_Type", "Product_Group", "Region"]))

# Combine features
X_train = pd.concat([
    train_df[["Category", "Bucket01", "Bucket24", "Bucket25", "BrandRxRatio", "RowCountPerHCP",
              "RX_Type_Diversity", "ChannelDiversity", "Is_Competitor", "Is_OwnBrand"]].reset_index(drop=True),
    encoded_train_df.reset_index(drop=True)
], axis=1)
y_train = train_df["Client_Data"]

# Train model
model = RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42)
model.fit(X_train, y_train)

#Exporting the model
joblib.dump(model, "hcp_encoder.pkl")
joblib.dump(encoder, "hcp_segmentation_model.pkl")