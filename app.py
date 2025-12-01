import streamlit as st
from blockchain import Blockchain
from generate_certificate import generate_pdf_certificate
from datetime import datetime
import os
import pandas as pd

# -------------------- Initialize Blockchain --------------------
if 'blockchain' not in st.session_state:
    st.session_state.blockchain = Blockchain()

blockchain = st.session_state.blockchain

# -------------------- Streamlit page settings --------------------
st.set_page_config(page_title="Blockchain Certificate System", page_icon="🎓", layout="wide")

# -------------------- Custom CSS / UI Enhancements --------------------
st.markdown("""
    <style>
    .main {background-color: #f8f9fa;}
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        height: 2.5em;
        width: 100%;
    }
    .stDownloadButton>button {
        background-color: #0d6efd;
        color: white;
        border-radius: 10px;
    }
    .stTextInput>div>input {
        height: 2em;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎓 Blockchain-Based Digital Certificate Verification System")
menu = ["🧾 Issue Certificate", "⛏️ Mine Block", "🔍 Verify Certificate", "📊 Admin Dashboard", "📜 View Blockchain"]
choice = st.sidebar.radio("Select Option", menu)

# -------------------- 🧾 Issue Certificate --------------------
if choice == "🧾 Issue Certificate":
    st.header("🧾 Issue New Certificate")

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("👤 Student Name")
        cert_id = st.text_input("🆔 Certificate ID (e.g., CERT001)")
        course = st.text_input("📘 Course Name")
    with col2:
        institution = st.text_input("🏫 College Name")
        today_date = datetime.now().strftime("%d/%m/%Y")
        date = st.text_input("📅 Issue Date (DD/MM/YYYY)", value=today_date)
        grade = st.selectbox("🏅 Grade", ["A+", "A", "B+", "B", "C", "D"], index=0)

    remarks = st.text_area("🗒️ Remarks", "Successfully completed the course with excellence.")

    if st.button("✅ Generate & Add to Blockchain"):
        if name and cert_id and course and institution:
            certificate_data = {
                "name": name,
                "cert_id": cert_id.strip().upper(),
                "course": course,
                "institution": institution,
                "date": date,
                "remarks": remarks,
                "grade": grade
            }
            # Add to blockchain pending transactions
            tx_index = blockchain.new_transaction(certificate_data)
            # Generate PDF certificate
            pdf_path = generate_pdf_certificate(
                **certificate_data,
                logo_path="ifet.png",
                signature_path="signature.png",
                verification_base_url="http://127.0.0.1:5000/verify"
            )
            st.success(f"✅ Certificate added to pending block #{tx_index} and PDF generated!")
            
            # Certificate Preview Before Download
            with open(pdf_path, "rb") as file:
                st.download_button("⬇️ Preview & Download Certificate", file, file_name=os.path.basename(pdf_path))
        else:
            st.error("Please fill all fields before generating!")

# -------------------- ⛏️ Mine Block --------------------
elif choice == "⛏️ Mine Block":
    st.header("⛏️ Mine Pending Certificates")
    if st.button("🚀 Mine Now"):
        last_block = blockchain.last_block
        proof = blockchain.proof_of_work(last_block["proof"])
        block = blockchain.new_block(proof, blockchain.hash(last_block))
        st.success("🎉 Block mined successfully!")
        st.json(block)

# -------------------- 🔍 Verify Certificate --------------------
elif choice == "🔍 Verify Certificate":
    st.header("🔍 Verify Certificate Authenticity")
    verify_cert_id = st.text_input("Enter Certificate ID to verify:")

    if st.button("🔍 Verify Now"):
        found = False
        cert_id_upper = verify_cert_id.strip().upper()

        # Check mined blocks
        for block in blockchain.chain:
            for cert in block.get("transactions", []):
                if cert.get("cert_id", "").strip().upper() == cert_id_upper:
                    st.success("✅ Certificate Found in Blockchain")
                    st.json(cert)
                    found = True
                    break
            if found:
                break

        # Check pending transactions
        if not found:
            for cert in blockchain.current_transactions:
                if cert.get("cert_id", "").strip().upper() == cert_id_upper:
                    st.info("ℹ️ Certificate is pending (not yet mined into a block)")
                    st.json(cert)
                    found = True
                    break

        if not found:
            st.error("❌ Certificate not found in blockchain records.")

# -------------------- 📊 Admin Dashboard --------------------
elif choice == "📊 Admin Dashboard":
    st.header("📊 Admin Analytics Dashboard")

    # Pending Certificates
    st.subheader("📝 Pending Certificates")
    if blockchain.current_transactions:
        st.table(blockchain.current_transactions)
    else:
        st.info("No pending certificates.")

    # Mined Certificates Analytics
    st.subheader("📈 Mined Certificates Analytics")
    mined_certs = []
    for block in blockchain.chain:
        mined_certs.extend(block.get("transactions", []))
    if mined_certs:
        df = pd.DataFrame(mined_certs)
        st.write("Total Certificates Issued:", len(df))
        st.bar_chart(df['grade'].value_counts())
        st.dataframe(df)
    else:
        st.info("No certificates mined yet.")

# -------------------- 📜 View Blockchain --------------------
elif choice == "📜 View Blockchain":
    st.header("📜 Full Blockchain Ledger")
    st.json(blockchain.chain)
