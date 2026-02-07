import streamlit as st
import requests

# Page Config
st.set_page_config(page_title="Enbox Provisioning", page_icon="⚡")

# Configuration from updated details
API_BASE_URL = "https://cmwvwqbrnxgofinkeevm.supabase.co/functions/v1/msp-api"
AUTH_HEADERS = {
    "x-msp-api-key": st.secrets["MSP_API_KEY"],
    "Content-Type": "application/json"
}

st.title("⚡ Enbox Account Creator")
st.info(f"Connected to: `{API_BASE_URL}`")

# Form Interface
with st.form("enbox_creation_form"):
    st.subheader("Account Details")
    
    col1, col2 = st.columns(2)
    with col1:
        email = st.text_input("Customer Email", placeholder="user@company.com")
        display_name = st.text_input("Display Name", placeholder="Acme Corp")
    
    with col2:
        create_via = st.selectbox("Creation Strategy", options=["direct", "invite"])
        # Password only shown/required if direct
        password = st.text_input("Password", type="password") if create_via == "direct" else None

    submitted = st.form_submit_button("🚀 Create Enbox")

# Request Execution
if submitted:
    # Validation
    if not email or not display_name:
        st.error("Email and Display Name are required.")
    elif create_via == "direct" and not password:
        st.error("Password is required for 'direct' creation.")
    else:
        # Construct Payload
        payload = {
            "email": email,
            "display_name": display_name,
            "create_via": create_via
        }
        if password:
            payload["password"] = password

        # API Call
        with st.spinner("Provisioning account..."):
            try:
                # Note: Appending /enboxes to the base URL as per your API spec
                response = requests.post(
                    f"{API_BASE_URL}/enboxes", 
                    headers=AUTH_HEADERS, 
                    json=payload
                )

                if response.status_code in [200, 201]:
                    st.success("✅ Account Created Successfully!")
                    st.json(response.json())
                else:
                    st.error(f"Failed (Status {response.status_code})")
                    st.write(response.text)
                    
            except Exception as e:
                st.exception(e)

# Helpful footer to check the endpoint
with st.expander("System Status"):
    st.write(f"Active Header: `x-msp-api-key: {st.secrets['MSP_API_KEY'][:4]}****`")
