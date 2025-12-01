# CertificateBlockchain Streamlit (Mini Project)

## Quick start
1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```
3. The app will open in your browser (http://localhost:8501)

## Features
- Issue certificate (generates a PDF + QR in certificates/static folders)
- Mine pending transactions into a new block (proof-of-work simulated)
- Verify a certificate by ID
- View full blockchain (stored in certificates.json)
