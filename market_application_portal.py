import os
import sqlite3
import json
import re
import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(
    page_title="Day & Night Market - Shop Application & Admin Portal",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        color: #ffffff;
        margin: 0;
        font-size: 26px;
        font-weight: 700;
    }
    .main-header p {
        color: #e0e0e0;
        margin: 5px 0 0 0;
        font-size: 14px;
    }
    .section-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #2a5298;
        margin-bottom: 20px;
    }
    .badge-pending {
        background-color: #ffeaa7; color: #d63031; padding: 4px 8px; border-radius: 4px; font-weight: bold;
    }
    .badge-approved {
        background-color: #55efc4; color: #00b894; padding: 4px 8px; border-radius: 4px; font-weight: bold;
    }
    .badge-rejected {
        background-color: #ff7675; color: #ffffff; padding: 4px 8px; border-radius: 4px; font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Database Setup - Portable path for Streamlit Cloud, local execution, and containers
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
DB_PATH = os.path.join(BASE_DIR, "market_applications.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_code TEXT UNIQUE,
            full_name TEXT,
            parent_spouse_name TEXT,
            whatsapp_no TEXT,
            other_contact TEXT,
            is_whatsapp_active TEXT,
            current_address TEXT,
            pincode TEXT,
            permanent_address TEXT,
            email TEXT,
            contact_time TEXT,
            shop_name TEXT,
            entity_type TEXT,
            operator_name TEXT,
            experience_status TEXT,
            main_shop_type TEXT,
            food_category TEXT,
            main_cuisines TEXT,
            unique_selling_point TEXT,
            signature_items TEXT,
            menu_flexibility TEXT,
            menu_items_json TEXT,
            preferred_hours TEXT,
            prep_method TEXT,
            amenities TEXT,
            est_investment REAL,
            expected_prep_days INTEGER,
            doc_availability TEXT,
            attachment_name TEXT,
            attachment_data BLOB,
            attachment_size INTEGER,
            digital_signature TEXT,
            submission_date TEXT,
            status TEXT DEFAULT 'Pending Review',
            admin_notes TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Regex Validations
def validate_mobile(number):
    return bool(re.match(r'^[6-9]\d{9}$', number.strip()))

def validate_pincode(pin):
    return bool(re.match(r'^\d{6}$', pin.strip()))

def validate_email(email):
    if not email.strip():
        return True
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email.strip()))

# Navigation Tabs
st.sidebar.title("📌 Navigation / नेविगेशन")
mode = st.sidebar.radio("Select View / दृश्य चुनें:", ["📝 Client Online Application Form", "🔐 Backend Admin Dashboard"])

if mode == "📝 Client Online Application Form":
    st.markdown("""
        <div class="main-header">
            <h1>🏪 दुकानदार आवेदन एवं KYC फॉर्म (Shop Application & KYC Form)</h1>
            <p>डे एंड नाइट मार्केट • जनेश्वर मिश्र पार्क के सामने • लखनऊ (Day & Night Market • Opp. Janeshwar Mishra Park • Lucknow)</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.info("ℹ️ यह फॉर्म दुकान/फूड काउंटर के लिए आपकी रुचि, अनुभव, प्रस्तावित मेन्यू और संपर्क विवरण जानने के लिए है। आवेदन देना दुकान का आवंटन या बुकिंग नहीं है।")

    with st.form("shop_application_form", clear_on_submit=False):
        
        # --- Section 1 ---
        st.subheader("1. आवेदक एवं संपर्क विवरण (Applicant & Contact Details)")
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("पूरा नाम (Full Name) *", placeholder="उदाहरण: राहुल शर्मा")
            whatsapp_no = st.text_input("WhatsApp मोबाइल नंबर (10-अंकीय) *", max_chars=10, placeholder="9876543210")
            is_whatsapp_active = st.radio("क्या दिए नंबर पर WhatsApp चलता है? *", ["हाँ (Yes)", "नहीं (No)"], horizontal=True)
            email = st.text_input("ईमेल (Email - Optional)", placeholder="name@example.com")
        with col2:
            parent_spouse_name = st.text_input("पिता / माता / पति / पत्नी का नाम (Parent/Spouse Name)")
            other_contact = st.text_input("अन्य संपर्क नंबर (Alternate Contact No.)", max_chars=10, placeholder="9876543211")
            contact_time = st.selectbox("संपर्क का सुविधाजनक समय (Convenient Contact Time)", ["सुबह (Morning)", "दोपहर (Afternoon)", "शाम (Evening)"])
        
        st.write("---")
        col3, col4 = st.columns(2)
        with col3:
            current_address = st.text_area("वर्तमान पूरा पता (Current Full Address) *", placeholder="मकान नं., गली, क्षेत्र...")
            pincode = st.text_input("पिन कोड (Pincode) *", max_chars=6, placeholder="226010")
        with col4:
            same_address = st.checkbox("स्थायी पता वर्तमान पते के समान है (Permanent Address same as Current)")
            if same_address:
                permanent_address = current_address
                st.text_area("स्थायी पता (Permanent Address)", value=current_address, disabled=True)
            else:
                permanent_address = st.text_area("स्थायी पता (Permanent Address)", placeholder="स्थायी पता दर्ज करें...")

        # --- Section 2 ---
        st.subheader("2. व्यवसाय की पहचान (Business Identification)")
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            shop_name = st.text_input("प्रस्तावित दुकान / ब्रांड / फर्म का नाम (Proposed Shop/Brand Name) *", placeholder="उदा. लखनऊ चाट कॉर्नर")
            entity_type = st.selectbox("स्वरूप (Entity Type) *", ["व्यक्तिगत (Individual)", "प्रोपराइटर (Proprietorship)", "साझेदारी (Partnership)", "कंपनी (Company)", "अभी तय नहीं (TBD)"])
        with col_b2:
            operator_name = st.text_input("वास्तविक संचालक और अधिकृत संपर्क व्यक्ति का नाम (यदि अलग हो)")

        # --- Section 3 ---
        st.subheader("3. कारोबार का अनुभव (Business Experience)")
        experience_status = st.radio(
            "आपकी स्थिति क्या है? (Current Experience Status) *",
            [
                "अभी दुकान चला रहे हैं (Currently running shop)",
                "पहले चलाई है, अभी बंद है (Previously ran, currently closed)",
                "होम किचन / कैटरिंग / ठेला चलाते हैं (Home Kitchen / Catering / Food Cart)",
                "पहली बार शुरू कर रहे हैं (First time starting)"
            ]
        )

        # --- Section 4 ---
        st.subheader("4. इस मार्केट में प्रस्तावित दुकान और मेन्यू (Proposed Shop & Menu)")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            main_shop_type = st.selectbox("दुकान का मुख्य प्रकार (Main Shop Category) *", ["फूड (Food)", "पेय पदार्थ (Beverage)", "फल / सब्जी (Fruits/Vegetables)", "किराना / रिटेल (Grocery/Retail)", "सेवा (Service)"])
            food_category = st.selectbox("फूड श्रेणी (Food Category) *", ["केवल शाकाहारी (Pure Veg)", "अंडा (Egg)", "नॉनवेज (Non-Veg)", "मिश्रित (Mixed)", "लागू नहीं (N/A)"])
        with col_m2:
            main_cuisines = st.text_input("मुख्य श्रेणी / व्यंजन (Main Cuisines, e.g. चाट, दक्षिण भारतीय, चाय) *")
            menu_flexibility = st.radio("मेन्यू पर चर्चा / बदलाव के लिए तैयार हैं? *", ["हाँ (Yes)", "नहीं (No)", "चर्चा के बाद (After Discussion)"], horizontal=True)

        unique_selling_point = st.text_area("इस मार्केट में आपकी दुकान की मुख्य पहचान / विशेषता क्या होगी? (Unique Specialty) *", placeholder="आपकी दुकान की क्या खासियत होगी...")
        signature_items = st.text_input("आपके 3 मुख्य / सिग्नेचर आइटम (3 Signature Items) *", placeholder="उदा. 1. स्पेशल बास्केट चाट, 2. कुल्हड़ चाय, 3. पनीर टिक्का")

        st.markdown("**प्रस्तावित मेन्यू / उत्पाद सूची (Proposed Menu Items):**")
        st.caption("नीचे दिए गए फ़ील्ड्स में अपने मुख्य आइटम भरें:")
        
        m_col1, m_col2, m_col3, m_col4 = st.columns([3, 2, 2, 2])
        menu_list = []
        for i in range(1, 4):
            with m_col1:
                item_name = st.text_input(f"आइटम {i} नाम", key=f"item_name_{i}")
            with m_col2:
                item_type = st.selectbox(f"प्रकार {i}", ["वेज", "नॉन-वेज", "पेय"], key=f"item_type_{i}")
            with m_col3:
                item_qty = st.text_input(f"मात्रा/सर्विंग {i}", placeholder="उदा. 1 प्लेट", key=f"item_qty_{i}")
            with m_col4:
                item_price = st.number_input(f"कीमत ₹ {i}", min_value=0, step=10, key=f"item_price_{i}")
            if item_name:
                menu_list.append({"item": item_name, "type": item_type, "qty": item_qty, "price": item_price})

        # --- Section 5 ---
        st.subheader("5. संचालन और आवश्यक सुविधाएँ (Operations & Required Amenities)")
        col_o1, col_o2 = st.columns(2)
        with col_o1:
            preferred_hours = st.selectbox("पसंदीदा समय (Preferred Operational Hours) *", ["सुबह (Morning)", "दिन (Day)", "शाम / रात (Evening/Night)", "पूरा संचालन समय (Full Operating Hours)"])
            prep_method = st.selectbox("तैयारी का तरीका (Preparation Method) *", ["दुकान पर पकाना (Cook on Shop)", "बाहर तैयार करके लाना (Cook outside)", "दोनों (Both)", "केवल पैक्ड सामान (Only Packed Items)"])
            est_investment = st.number_input("प्रारंभिक निवेश का अनुमान (Estimated Initial Investment in ₹) *", min_value=10000, step=10000, value=100000)
        with col_o2:
            expected_prep_days = st.number_input("तैयारी हेतु अपेक्षित समय (Expected Setup Days) *", min_value=1, max_value=180, value=15)
            amenities_selected = st.multiselect(
                "जरूरी सुविधाएँ (Required Amenities)",
                ["पानी (Water)", "ड्रेनेज (Drainage)", "LPG", "इंडक्शन (Induction)", "एग्जॉस्ट (Exhaust)", "फ्रिज / फ्रीजर (Refrigerator/Freezer)"]
            )

        # --- Section 6 ---
        st.subheader("6. दस्तावेज उपलब्धता, अटैचमेंट एवं घोषणा (Documents, Attachment & Declaration)")
        doc_availability = st.selectbox("दस्तावेज उपलब्धता (KYC Documents Availability) *", ["उपलब्ध है (Available)", "प्रक्रिया में (In Progress)", "उपलब्ध नहीं (Not Available)"])
        
        # Attachment with 2MB Max Validation Requirement
        st.markdown("**📎 KYC / दस्तावेज / मेन्यू फ़ाइल अटैच करें (Attach KYC Document / Menu / Shop Photo)**")
        st.caption("⚠️ **अधिकतम फ़ाइल साइज़: 2 MB (Max File Size: 2 MB)** | स्वीकार्य फ़ाइल प्रारूप: PDF, JPG, PNG")
        uploaded_file = st.file_uploader("फ़ाइल चुनें (Choose File)", type=["pdf", "jpg", "jpeg", "png"])
        
        st.markdown("**घोषणा चेकबॉक्स (Declaration Checkboxes):**")
        dec1 = st.checkbox("मैं पुष्टि करता/करती हूँ कि दी गई जानकारी मेरी जानकारी के अनुसार सही है। मैं आवेदन की जाँच, मेन्यू चर्चा और संपर्क के लिए प्रबंधन को कॉल/WhatsApp करने की अनुमति देता/देती हूँ। *")
        dec2 = st.checkbox("मैं समझता/समझती हूँ कि यह केवल रुचि आवेदन है। आवंटन, मेन्यू, शुल्क और अन्य शर्तें लिखित स्वीकृति/समझौते से तय होंगी। *")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            digital_signature = st.text_input("आवेदक का नाम (डिजिटल हस्ताक्षर / Digital Signature) *", placeholder="अपना पूरा नाम लिखें")
        with col_s2:
            sub_date = st.date_input("दिनांक (Date)")

        submit_btn = st.form_submit_button("🚀 आवेदन जमा करें (Submit Application)")

    if submit_btn:
        # Validation checks
        errors = []
        if not full_name.strip():
            errors.append("कृपया आवेदक का पूरा नाम दर्ज करें (Applicant Full Name is required).")
        if not whatsapp_no.strip() or not validate_mobile(whatsapp_no):
            errors.append("कृपया वैध 10-अंकीय WhatsApp मोबाइल नंबर दर्ज करें (Valid 10-digit Mobile Number required).")
        if not current_address.strip():
            errors.append("कृपया वर्तमान पूरा पता दर्ज करें (Current Address is required).")
        if not pincode.strip() or not validate_pincode(pincode):
            errors.append("कृपया वैध 6-अंकीय पिन कोड दर्ज करें (Valid 6-digit Pincode required).")
        if email.strip() and not validate_email(email):
            errors.append("कृपया वैध ईमेल पता दर्ज करें (Valid Email format required).")
        if not shop_name.strip():
            errors.append("कृपया प्रस्तावित दुकान/ब्रांड का नाम दर्ज करें (Proposed Shop Name is required).")
        if not unique_selling_point.strip():
            errors.append("कृपया दुकान की मुख्य पहचान/विशेषता दर्ज करें (Unique Specialty required).")
        if not signature_items.strip():
            errors.append("कृपया 3 मुख्य/सिग्नेचर आइटम दर्ज करें (Signature Items required).")
        if not dec1 or not dec2:
            errors.append("कृपया दोनों घोषणा चेकबॉक्स स्वीकार करें (Please check both declaration boxes).")
        if not digital_signature.strip():
            errors.append("कृपया अपना डिजिटल हस्ताक्षर दर्ज करें (Digital Signature is required).")

        # Attachment 2MB Size Validation
        attachment_name = None
        attachment_data = None
        attachment_size = 0
        if uploaded_file is not None:
            attachment_size = uploaded_file.size
            if attachment_size > 2 * 1024 * 1024: # 2MB limit
                errors.append(f"🛑 फ़ाइल का आकार 2 MB से अधिक है ({attachment_size / (1024*1024):.2f} MB)। कृपया 2 MB से छोटी फ़ाइल अपलोड करें! (File exceeds 2 MB size limit).")
            else:
                attachment_name = uploaded_file.name
                attachment_data = uploaded_file.read()

        if errors:
            for err in errors:
                st.error(f"❌ {err}")
        else:
            # Generate Application Code
            import random
            app_code = f"DNM-2026-{random.randint(1000, 9999)}"
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO applications (
                    app_code, full_name, parent_spouse_name, whatsapp_no, other_contact, is_whatsapp_active,
                    current_address, pincode, permanent_address, email, contact_time, shop_name, entity_type,
                    operator_name, experience_status, main_shop_type, food_category, main_cuisines,
                    unique_selling_point, signature_items, menu_flexibility, menu_items_json, preferred_hours,
                    prep_method, amenities, est_investment, expected_prep_days, doc_availability,
                    attachment_name, attachment_data, attachment_size, digital_signature, submission_date, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                app_code, full_name, parent_spouse_name, whatsapp_no, other_contact, is_whatsapp_active,
                current_address, pincode, permanent_address, email, contact_time, shop_name, entity_type,
                operator_name, experience_status, main_shop_type, food_category, main_cuisines,
                unique_selling_point, signature_items, menu_flexibility, json.dumps(menu_list), preferred_hours,
                prep_method, ", ".join(amenities_selected), est_investment, expected_prep_days, doc_availability,
                attachment_name, attachment_data, attachment_size, digital_signature, str(sub_date), "Pending Review"
            ))
            conn.commit()
            conn.close()

            st.success(f"🎉 **आवेदन सफलतापूर्वक जमा हो गया है! (Application Submitted Successfully!)**\n\n**आपका आवेदन कोड (Application Code):** `{app_code}`")
            st.balloons()

# --- BACKEND ADMIN DASHBOARD ---
else:
    st.markdown("""
        <div class="main-header" style="background: linear-gradient(135deg, #000428 0%, #004e92 100%);">
            <h1>🔐 बैकएंड एडमिन पोर्टल (Backend Admin Portal & Dashboard)</h1>
            <p>डे एंड नाइट मार्केट • दुकान आवेदन समीक्षा एवं प्रबंधन (Application Review & Management)</p>
        </div>
    """, unsafe_allow_html=True)

    # Simple Session Authentication
    if 'admin_logged_in' not in st.session_state:
        st.session_state['admin_logged_in'] = False

    if not st.session_state['admin_logged_in']:
        st.subheader("🔑 एडमिन लॉगिन (Admin Login)")
        with st.form("login_form"):
            user = st.text_input("Username / यूज़रनेम", value="admin")
            pwd = st.text_input("Password / पासवर्ड", type="password", value="market123")
            login_btn = st.form_submit_button("लॉगिन करें (Login)")
            
            if login_btn:
                if user == "admin" and pwd == "market123":
                    st.session_state['admin_logged_in'] = True
                    st.rerun()
                else:
                    st.error("❌ अमान्य यूज़रनेम या पासवर्ड! (Invalid Username or Password)")
        st.info("💡 डेमो क्रेडेंशियल (Demo Credentials): Username: `admin` | Password: `market123`")
    else:
        st.sidebar.success("✅ Logged in as Admin")
        if st.sidebar.button("🔒 Logout"):
            st.session_state['admin_logged_in'] = False
            st.rerun()

        # Fetch Data
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT id, app_code, full_name, whatsapp_no, shop_name, main_shop_type, food_category, est_investment, submission_date, status, attachment_name, attachment_size FROM applications ORDER BY id DESC", conn)
        conn.close()

        # KPI Overview
        st.subheader("📊 आवेदन समीक्षा डैशबोर्ड (Overview Analytics)")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("कुल आवेदन (Total Applications)", len(df))
        m2.metric("लंबित समीक्षा (Pending Review)", len(df[df['status'] == 'Pending Review']) if not df.empty else 0)
        m3.metric("स्वीकृत आवेदन (Approved)", len(df[df['status'] == 'Approved']) if not df.empty else 0)
        m4.metric("कुल प्रस्तावित निवेश (Total Proposed Investment)", f"₹ {df['est_investment'].sum():,.0f}" if not df.empty else "₹ 0")

        st.write("---")

        # Search & Filter
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            search_query = st.text_input("🔍 नाम / कोड / मोबाइल से खोजें (Search)", "")
        with col_f2:
            status_filter = st.selectbox("फिल्टर स्थिति (Filter Status)", ["All", "Pending Review", "Approved", "Under Review", "Rejected"])
        with col_f3:
            category_filter = st.selectbox("फिल्टर श्रेणी (Filter Shop Category)", ["All", "फूड (Food)", "पेय पदार्थ (Beverage)", "फल / सब्जी (Fruits/Vegetables)", "किराना / रिटेल (Grocery/Retail)", "सेवा (Service)"])

        filtered_df = df.copy()
        if search_query:
            filtered_df = filtered_df[
                filtered_df['full_name'].str.contains(search_query, case=False, na=False) |
                filtered_df['app_code'].str.contains(search_query, case=False, na=False) |
                filtered_df['whatsapp_no'].str.contains(search_query, case=False, na=False) |
                filtered_df['shop_name'].str.contains(search_query, case=False, na=False)
            ]
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df['status'] == status_filter]
        if category_filter != "All":
            filtered_df = filtered_df[filtered_df['main_shop_type'] == category_filter]

        st.subheader("📋 आवेदन सूची (Applications List)")
        if filtered_df.empty:
            st.warning("कोई आवेदन नहीं मिला। (No applications found.)")
        else:
            # Format display dataframe
            display_df = filtered_df[['app_code', 'full_name', 'whatsapp_no', 'shop_name', 'main_shop_type', 'food_category', 'est_investment', 'submission_date', 'status', 'attachment_name']].copy()
            display_df.columns = ['Application Code', 'Applicant Name', 'WhatsApp No', 'Shop Name', 'Category', 'Food Type', 'Investment (₹)', 'Date', 'Status', 'Attachment']
            st.dataframe(display_df, use_container_width=True)

            # Detail View Selector
            st.write("---")
            st.subheader("🔎 विस्तृत आवेदन देखें एवं स्थिति बदलें (Detailed View & Status Action)")
            selected_app_code = st.selectbox("समीक्षा के लिए आवेदन कोड चुनें (Select Application Code to Review):", filtered_df['app_code'].tolist())
            
            if selected_app_code:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM applications WHERE app_code = ?", (selected_app_code,))
                app_data = cursor.fetchone()
                columns = [col[0] for col in cursor.description]
                conn.close()

                app_dict = dict(zip(columns, app_data))

                st.markdown(f"### 📄 विवरण: `{app_dict['app_code']}` - {app_dict['shop_name']}")
                
                c_d1, c_d2 = st.columns(2)
                with c_d1:
                    st.markdown(f"**आवेदक का नाम:** {app_dict['full_name']}")
                    st.markdown(f"**अभिभावक/पति का नाम:** {app_dict['parent_spouse_name'] or 'N/A'}")
                    st.markdown(f"**WhatsApp नंबर:** {app_dict['whatsapp_no']} (WhatsApp Active: {app_dict['is_whatsapp_active']})")
                    st.markdown(f"**अन्य संपर्क:** {app_dict['other_contact'] or 'N/A'}")
                    st.markdown(f"**ईमेल:** {app_dict['email'] or 'N/A'}")
                    st.markdown(f"**वर्तमान पता:** {app_dict['current_address']} (Pin: {app_dict['pincode']})")
                    st.markdown(f"**स्थायी पता:** {app_dict['permanent_address']}")
                
                with c_d2:
                    st.markdown(f"**प्रस्तावित दुकान का नाम:** {app_dict['shop_name']}")
                    st.markdown(f"**स्वरूप (Entity):** {app_dict['entity_type']}")
                    st.markdown(f"**संचालक:** {app_dict['operator_name'] or 'N/A'}")
                    st.markdown(f"**अनुभव की स्थिति:** {app_dict['experience_status']}")
                    st.markdown(f"**मुख्य श्रेणी:** {app_dict['main_shop_type']} | **फूड श्रेणी:** {app_dict['food_category']}")
                    st.markdown(f"**प्रस्तावित निवेश:** ₹ {app_dict['est_investment']:,.0f}")
                    st.markdown(f"**तैयारी का समय:** {app_dict['expected_prep_days']} दिन")

                st.write("---")
                st.markdown(f"**विशेषता (USP):** {app_dict['unique_selling_point']}")
                st.markdown(f"**3 सिग्नेचर आइटम:** {app_dict['signature_items']}")
                st.markdown(f"**जरूरी सुविधाएँ:** {app_dict['amenities'] or 'None'}")

                # Display Menu Table
                if app_dict['menu_items_json']:
                    try:
                        menu_items = json.loads(app_dict['menu_items_json'])
                        if menu_items:
                            st.markdown("**प्रस्तावित मेन्यू सूची (Proposed Menu Items):**")
                            st.table(pd.DataFrame(menu_items))
                    except:
                        pass

                # Display Attachment
                st.write("---")
                st.markdown("### 📎 संलग्न फ़ाइल (Uploaded Attachment)")
                if app_dict['attachment_name'] and app_dict['attachment_data']:
                    st.success(f"📎 **फ़ाइल नाम:** `{app_dict['attachment_name']}` (साइज़: {app_dict['attachment_size']/1024:.1f} KB)")
                    st.download_button(
                        label="⬇️ संलग्न फ़ाइल डाउनलोड करें (Download Attachment)",
                        data=app_dict['attachment_data'],
                        file_name=app_dict['attachment_name'],
                        mime="application/octet-stream"
                    )
                else:
                    st.info("ℹ️ इस आवेदन में कोई फ़ाइल संलग्न नहीं है। (No attachment uploaded for this application.)")

                # Action Box
                st.write("---")
                st.markdown("### 🛠️ स्थिति अद्यतन एवं एडमिन टिप्पणियाँ (Update Status & Admin Notes)")
                with st.form("status_update_form"):
                    new_status = st.selectbox("आवेदन की स्थिति बदलें (Change Status):", ["Pending Review", "Approved", "Under Review", "Rejected"], index=["Pending Review", "Approved", "Under Review", "Rejected"].index(app_dict['status']))
                    admin_notes = st.text_area("एडमिन टिप्पणी (Admin Notes):", value=app_dict['admin_notes'] or "")
                    update_btn = st.form_submit_button("💾 परिवर्तन सहेजें (Save Updates)")

                    if update_btn:
                        conn = sqlite3.connect(DB_PATH)
                        cursor = conn.cursor()
                        cursor.execute("UPDATE applications SET status = ?, admin_notes = ? WHERE app_code = ?", (new_status, admin_notes, selected_app_code))
                        conn.commit()
                        conn.close()
                        st.success(f"✅ आवेदन `{selected_app_code}` की स्थिति `{new_status}` में अद्यतन हो गई है!")
                        st.rerun()

        # CSV Export Option
        st.write("---")
        if not df.empty:
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 सभी आवेदन CSV में डाउनलोड करें (Export All Applications to CSV)",
                data=csv_data,
                file_name="day_and_night_market_applications.csv",
                mime="text/csv"
            )
