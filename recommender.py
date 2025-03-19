import streamlit as st
import pandas as pd

# Cache the data loading function for performance
@st.cache_data
def load_data():
    df = pd.read_excel('./data/ey_vehicle.xlsx')
    
    # Select only the columns that matter for our matching
    selected_columns = [
        'ey_brandname',        # Car make
 #       'ey_modelkeyidname',   # Model key name (replaces ey_modeltext)
        'ey_vehiclemodelidname',# Additional model identifier
        'ey_bodyworktypename', # Bodywork type (replaces ey_bodytypename)
        'ey_vehiclecolorname', # Vehicle color
        'ey_transmissionname', # Transmission type
        'ey_enginepower',      # Engine power (numeric)
        'ey_fueltypename',     # Fuel type
        'ey_productionyear',   # Production year
        'ey_trimlinename',     # Trim line
        'ey_mileage'           # Mileage
    ]
    
    # Keep only those columns if they exist in the dataframe
    available_columns = [col for col in selected_columns if col in df.columns]
    return df[available_columns]

df = load_data()

# Helper to get unique options for categorical columns and prepend a blank value.
def get_options(col):
    if col not in df.columns:
        return [""]
    options = sorted(df[col].dropna().unique().tolist())
    return [""] + options  # Prepend an empty option

st.title("EY Lead2Car Configurator Recommender")

st.write("Configure your desired car attributes in the side panel on the left.⬅️")

# Sidebar EY logo
st.sidebar.image("./data/ey_logo.png", use_container_width=True)

# Create user input fields based on the columns we have
configured_car = {}

# 1. Brand (categorical)
brand_options = get_options('ey_brandname')
if brand_options:
    configured_car['ey_brandname'] = st.sidebar.selectbox("Brand", options=brand_options)
else:
    configured_car['ey_brandname'] = ""



# 3. Bodywork type (categorical)
bodywork_options = get_options('ey_bodyworktypename')
if bodywork_options:
    configured_car['ey_bodyworktypename'] = st.sidebar.selectbox("Bodywork Type", options=bodywork_options)
else:
    configured_car['ey_bodyworktypename'] = ""

# 4. Vehicle color (categorical)
color_options = get_options('ey_vehiclecolorname')
if color_options:
    configured_car['ey_vehiclecolorname'] = st.sidebar.selectbox("Color", options=color_options)
else:
    configured_car['ey_vehiclecolorname'] = ""

# 5. Transmission (categorical)
transmission_options = get_options('ey_transmissionname')
if transmission_options:
    configured_car['ey_transmissionname'] = st.sidebar.selectbox("Transmission", options=transmission_options)
else:
    configured_car['ey_transmissionname'] = ""

# 6. Vehicle Model ID name (categorical)
modelid_options = get_options('ey_vehiclemodelidname')
if modelid_options:
    configured_car['ey_vehiclemodelidname'] = st.sidebar.selectbox("Vehicle Model ID", options=modelid_options)
else:
    configured_car['ey_vehiclemodelidname'] = ""

# 7. Trim line (categorical)
trim_options = get_options('ey_trimlinename')
if trim_options:
    configured_car['ey_trimlinename'] = st.sidebar.selectbox("Trim Line", options=trim_options)
else:
    configured_car['ey_trimlinename'] = ""

# 8. Fuel type (categorical)
fuel_options = get_options('ey_fueltypename')
if fuel_options:
    configured_car['ey_fueltypename'] = st.sidebar.selectbox("Fuel Type", options=fuel_options)
else:
    configured_car['ey_fueltypename'] = ""

# 9. Engine power (numeric)
configured_car['ey_enginepower'] = st.sidebar.number_input("Engine Power", min_value=0, step=1, value=140)

# 10. Production year (numeric)
configured_car['ey_productionyear'] = st.sidebar.number_input("Production Year", min_value=1900, max_value=2050, step=1, value=2020)

# 11. Mileage (numeric)
configured_car['ey_mileage'] = st.sidebar.number_input("Mileage (km)", min_value=0, step=1000, value=50000)

# Define weights for each attribute based on their importance
attribute_weights = {
    'ey_brandname':         0.40,
    #'ey_modelkeyidname':    0.10,
    'ey_bodyworktypename':  0.10,
    'ey_vehiclecolorname':  0.10,
    'ey_transmissionname':  0.10,
    'ey_vehiclemodelidname':0.20,
    'ey_trimlinename':      0.10,
    'ey_enginepower':       0.05,
    'ey_fueltypename':      0.05,
    'ey_productionyear':    0.10,
    'ey_mileage':           0.05
}

def calculate_similarity(row, config, weights):
    score = 0.0
    
    # List of categorical columns
    categorical_attrs = [
        'ey_brandname',
        'ey_modelkeyidname',
        'ey_bodyworktypename',
        'ey_vehiclecolorname',
        'ey_transmissionname',
        'ey_vehiclemodelidname',
        'ey_trimlinename',
        'ey_fueltypename'
    ]
    
    # For categorical attributes, add full weight if there is an exact match
    for attr in categorical_attrs:
        if attr in row and pd.notnull(row[attr]) and row[attr] == config[attr]:
            score += weights[attr]
    

    # Numeric attributes: enginepower, productionyear, mileage
    # Adjust the thresholds as needed for your use case

    # 1. Engine Power
    if 'ey_enginepower' in row and pd.notnull(row['ey_enginepower']):
        diff = abs(row['ey_enginepower'] - config['ey_enginepower'])
        # Example threshold: 50 HP difference for zero credit
        if diff < 50:
            score += weights['ey_enginepower'] * (1 - diff / 50)
    
    # 2. Production Year
    if 'ey_productionyear' in row and pd.notnull(row['ey_productionyear']):
        year_diff = abs(row['ey_productionyear'] - config['ey_productionyear'])
        # Example threshold: 5 years difference for zero credit
        if year_diff < 5:
            score += weights['ey_productionyear'] * (1 - year_diff / 5)
    
    # 3. Mileage
    if 'ey_mileage' in row and pd.notnull(row['ey_mileage']):
        mileage_diff = abs(row['ey_mileage'] - config['ey_mileage'])
        # Example threshold: 50,000 km difference for zero credit
        if mileage_diff < 50000:
            score += weights['ey_mileage'] * (1 - mileage_diff / 50000)
    
    return score

st.markdown(
    """
    <style>
    div.stButton > button {
        background-color: #FFC107;  /* EY Yellow */
        color: black;
    }
    </style>
    """, unsafe_allow_html=True
)

if st.button("Get Recommendations"):
    # Compute similarity score for each vehicle
    df['similarity_score'] = df.apply(
        lambda row: calculate_similarity(row, configured_car, attribute_weights), axis=1
    )
    
    # Sort by similarity score (descending)
    recommendations = df.sort_values(by='similarity_score', ascending=False)
    
    st.subheader("Top Recommended Vehicles")
    st.write(recommendations.head(10))
