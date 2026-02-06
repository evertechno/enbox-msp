import streamlit as st
import requests
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="MSP Enbox Manager",
    page_icon="📧",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.25rem;
        color: #721c24;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.25rem;
        color: #0c5460;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.markdown('<div class="main-header">📧 MSP Enbox Manager</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Programmatically manage your customer Enboxes</div>', unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "https://vwhxcuylitpawxjplfnq.supabase.co/functions/v1/msp-gateway"

def get_api_key():
    """Get API key from Streamlit secrets"""
    try:
        return st.secrets["msp"]["api_key"]
    except Exception as e:
        st.error("⚠️ MSP API key not found in secrets. Please configure it in .streamlit/secrets.toml")
        st.code("""
# Add this to .streamlit/secrets.toml:
[msp]
api_key = "msp_your_key_here"
        """, language="toml")
        return None

def make_api_request(method, endpoint, data=None):
    """Make API request with proper authentication"""
    api_key = get_api_key()
    if not api_key:
        return None, "API key not configured"
    
    url = f"{API_BASE_URL}{endpoint}"
    headers = {
        "x-msp-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        else:
            return None, f"Unsupported method: {method}"
        
        return response, None
    except Exception as e:
        return None, str(e)

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Action", ["Create Enbox", "List Enboxes", "API Documentation"])

# Create Enbox Page
if page == "Create Enbox":
    st.header("Create New Managed Enbox")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("create_enbox_form"):
            st.subheader("Account Details")
            
            email = st.text_input(
                "Email Address *",
                placeholder="customer@example.com",
                help="The email address for the new Enbox account"
            )
            
            display_name = st.text_input(
                "Display Name *",
                placeholder="Customer Name",
                help="The display name for the customer"
            )
            
            create_via = st.radio(
                "Account Creation Method *",
                options=["direct", "invite"],
                help="Direct: Create with password | Invite: Send invitation email"
            )
            
            password = ""
            if create_via == "direct":
                password = st.text_input(
                    "Password *",
                    type="password",
                    placeholder="Enter a secure password",
                    help="Required for direct account creation"
                )
                
                password_confirm = st.text_input(
                    "Confirm Password *",
                    type="password",
                    placeholder="Re-enter the password"
                )
            
            st.markdown("---")
            submitted = st.form_submit_button("Create Enbox", use_container_width=True)
            
            if submitted:
                # Validation
                errors = []
                
                if not email or "@" not in email:
                    errors.append("Valid email address is required")
                
                if not display_name:
                    errors.append("Display name is required")
                
                if create_via == "direct":
                    if not password:
                        errors.append("Password is required for direct creation")
                    elif len(password) < 8:
                        errors.append("Password must be at least 8 characters long")
                    elif password != password_confirm:
                        errors.append("Passwords do not match")
                
                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                else:
                    # Prepare payload
                    payload = {
                        "email": email,
                        "display_name": display_name,
                        "create_via": create_via
                    }
                    
                    if create_via == "direct":
                        payload["password"] = password
                    
                    # Make API request
                    with st.spinner("Creating Enbox account..."):
                        response, error = make_api_request("POST", "/enboxes", payload)
                        
                        if error:
                            st.error(f"❌ Error: {error}")
                        elif response:
                            if response.status_code in [200, 201]:
                                st.success("✅ Enbox account created successfully!")
                                
                                # Display response data
                                try:
                                    result = response.json()
                                    st.json(result)
                                except:
                                    st.write(response.text)
                                
                                # Clear form (rerun)
                                st.balloons()
                            else:
                                st.error(f"❌ Error {response.status_code}: {response.text}")
    
    with col2:
        st.info("""
        ### 📋 Quick Guide
        
        **Direct Creation:**
        - Creates account immediately
        - Requires password
        - User can log in right away
        
        **Invite Creation:**
        - Sends invitation email
        - User sets own password
        - More secure for distribution
        
        **Tips:**
        - Use strong passwords (8+ chars)
        - Use invite for better security
        - Verify email format
        """)

# List Enboxes Page
elif page == "List Enboxes":
    st.header("Managed Enboxes")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button("🔄 Refresh List", use_container_width=True):
            st.rerun()
    
    with st.spinner("Fetching Enboxes..."):
        response, error = make_api_request("GET", "/enboxes")
        
        if error:
            st.error(f"❌ Error: {error}")
        elif response:
            if response.status_code == 200:
                try:
                    enboxes = response.json()
                    
                    if isinstance(enboxes, list):
                        if len(enboxes) == 0:
                            st.info("📭 No Enboxes found. Create your first one using the 'Create Enbox' page.")
                        else:
                            st.success(f"✅ Found {len(enboxes)} Enbox(es)")
                            
                            # Display as table
                            for idx, enbox in enumerate(enboxes, 1):
                                with st.expander(f"📧 {enbox.get('email', 'Unknown')} - {enbox.get('display_name', 'N/A')}"):
                                    cols = st.columns(2)
                                    
                                    with cols[0]:
                                        st.write("**Email:**", enbox.get('email', 'N/A'))
                                        st.write("**Display Name:**", enbox.get('display_name', 'N/A'))
                                    
                                    with cols[1]:
                                        st.write("**Created Via:**", enbox.get('create_via', 'N/A'))
                                        if 'created_at' in enbox:
                                            st.write("**Created:**", enbox['created_at'])
                                    
                                    st.json(enbox)
                    else:
                        st.json(enboxes)
                        
                except Exception as e:
                    st.error(f"Error parsing response: {e}")
                    st.write(response.text)
            else:
                st.error(f"❌ Error {response.status_code}: {response.text}")

# API Documentation Page
else:
    st.header("API Documentation")
    
    st.markdown("""
    ### Authentication
    
    Include your MSP API key in the `x-msp-api-key` header.
    """)
    
    st.code("""
curl -H "x-msp-api-key: msp_your_key_here" \\
  https://vwhxcuylitpawxjplfnq.supabase.co/functions/v1/msp-gateway/enboxes
    """, language="bash")
    
    st.markdown("---")
    
    st.subheader("Endpoints")
    
    # GET /enboxes
    with st.expander("GET /enboxes - List all managed Enboxes"):
        st.markdown("**Description:** Retrieve a list of all your managed Enboxes")
        
        st.code("""
curl -H "x-msp-api-key: msp_your_key_here" \\
  https://vwhxcuylitpawxjplfnq.supabase.co/functions/v1/msp-gateway/enboxes
        """, language="bash")
    
    # POST /enboxes
    with st.expander("POST /enboxes - Create a new managed Enbox"):
        st.markdown("**Description:** Create a new managed Enbox account")
        
        st.markdown("**Request Body:**")
        st.code("""
{
  "email": "customer@example.com",
  "password": "securepass123",  // Only for create_via: "direct"
  "display_name": "Customer Name",
  "create_via": "direct" | "invite"
}
        """, language="json")
        
        st.markdown("**Example cURL:**")
        st.code("""
curl -X POST \\
  -H "x-msp-api-key: msp_your_key_here" \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "customer@example.com",
    "password": "securepass123",
    "display_name": "Customer Name",
    "create_via": "direct"
  }' \\
  https://vwhxcuylitpawxjplfnq.supabase.co/functions/v1/msp-gateway/enboxes
        """, language="bash")
    
    st.markdown("---")
    
    st.subheader("Configuration")
    
    st.markdown("""
    This application uses Streamlit secrets for API key management. 
    
    Create a file `.streamlit/secrets.toml` with:
    """)
    
    st.code("""
[msp]
api_key = "msp_your_key_here"
    """, language="toml")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.8rem;'>
        <p>MSP Enbox Manager v1.0</p>
        <p>Manage your customer Enboxes efficiently</p>
    </div>
""", unsafe_allow_html=True)
