# verify_server.py
from flask import Flask, request, jsonify
from blockchain import Blockchain

app = Flask(__name__)
blockchain = Blockchain()  # Same blockchain structure as Streamlit app

@app.route('/verify', methods=['GET'])
def verify_certificate():
    cert_id = request.args.get('cert_id', '').strip().upper()
    if not cert_id:
        return jsonify({"status": "error", "message": "Certificate ID required"}), 400

    # Search mined blocks
    for block in blockchain.chain:
        for cert in block.get("transactions", []):
            if cert.get("cert_id", "").strip().upper() == cert_id:
                return jsonify({
                    "status": "success",
                    "message": "Certificate found in blockchain",
                    "certificate": cert
                })

    # Check pending transactions
    for cert in blockchain.current_transactions:
        if cert.get("cert_id", "").strip().upper() == cert_id:
            return jsonify({
                "status": "pending",
                "message": "Certificate is pending (not yet mined)",
                "certificate": cert
            })

    return jsonify({"status": "error", "message": "Certificate not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
