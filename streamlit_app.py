import streamlit as st
import requests

# App configuration
st.set_page_config(page_title="MSP Enbox Manager", page_icon="✉️")

# API Constants
API_URL = "https://vwhxcuylitpawxjplfnq.supabase.co/functions/v1/msp-gateway/enboxes"
HEADERS = {
    "x-msp-api-key": st.secrets["MSP_API_KEY"],
    "Content-Type": "application/json"
}

st.title("✉️ MSP Enbox Manager")
st.markdown("Use this interface to programmatically manage customer Enboxes.")

# --- Sidebar: List Existing Enboxes ---
with st.sidebar:
    st.header("Existing Enboxes")
    if st.button("Refresh List"):
        try:
            response = requests.get(API_URL, headers=HEADERS)
            if response.status_code == 200:
                enboxes = response.json()
                st.write(enboxes)
            else:
                st.error(f"Failed to fetch: {response.status_code}")
        except Exception as e:
            st.error(f"Error: {e}")

# --- Main Interface: Create New Enbox ---
st.subheader("Create a New Managed Enbox")

with st.form("create_enbox_form"):
    email = st.text_input("Customer Email", placeholder="customer@example.com")
    display_name = st.text_input("Display Name", placeholder="Customer Name")
    
    # Selection for create_via
    create_via = st.selectbox("Creation Method", options=["direct", "invite"])
    
    # Conditional password field
    password = ""
    if create_via == "direct":
        password = st.text_input("Password", type="password", help="Required for direct creation")
    
    submit_button = st.form_submit_button("Create Enbox")

# --- Logic to handle submission ---
if submit_button:
    if not email or not display_name:
        st.warning("Please fill in the email and display name.")
    elif create_via == "direct" and not password:
        st.warning("Password is required for 'direct' creation.")
    else:
        # Prepare payload
        payload = {
            "email": email,
            "display_name": display_name,
            "create_via": create_via
        }
        if create_via == "direct":
            payload["password"] = password

        with st.spinner("Creating Enbox..."):
            try:
                response = requests.post(API_URL, headers=HEADERS, json=payload)
                
                if response.status_code in [200, 201]:
                    st.success(f"Successfully created Enbox for {email}!")
                    st.balloons()
                    st.json(response.json())
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")
