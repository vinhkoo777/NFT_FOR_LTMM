import json, os
from decimal import Decimal
from dotenv import load_dotenv
from flask import Flask, render_template, request
from web3 import Web3

load_dotenv()

RPC_URL = os.getenv("RPC_URL")
CHAIN_ID = int(os.getenv("CHAIN_ID", "1337"))
ADDR_MY_NFT = Web3.to_checksum_address(os.getenv("ADDR_MY_NFT"))
ADDR_MARKET = Web3.to_checksum_address(os.getenv("ADDR_MARKET"))

PK_SELLER = os.getenv("PRIVATE_KEY_SELLER")
PK_BUYER = os.getenv("PRIVATE_KEY_BUYER")

w3 = Web3(Web3.HTTPProvider(RPC_URL))
assert w3.is_connected(), "Không kết nối được RPC Ganache"

with open("abi/MyNFT.json") as f:
    ABI_NFT = json.load(f)
with open("abi/Marketplace.json") as f:
    ABI_MK = json.load(f)

c_nft = w3.eth.contract(address=ADDR_MY_NFT, abi=ABI_NFT)
c_mk = w3.eth.contract(address=ADDR_MARKET, abi=ABI_MK)

acct_seller = w3.eth.account.from_key(PK_SELLER)
acct_buyer  = w3.eth.account.from_key(PK_BUYER)

# Debug do sợ t sẽ sai sót một cái gì đó hehe
print("Connected:", w3.is_connected())
print("Chain id (node):", w3.eth.chain_id)
print("ADDR_MY_NFT:", ADDR_MY_NFT)
print("Code at NFT addr:", w3.eth.get_code(ADDR_MY_NFT).hex())
print("Code at MARKET addr:", w3.eth.get_code(ADDR_MARKET).hex())
print("Seller:", acct_seller.address, "balance:", w3.from_wei(w3.eth.get_balance(acct_seller.address),'ether'))
print("Buyer:", acct_buyer.address,   "balance:", w3.from_wei(w3.eth.get_balance(acct_buyer.address),'ether'))

# ---- Helper ----
def _build_and_send_tx(account, tx):
    signed = account.sign_transaction(tx)
    txh = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(txh)
    return receipt.transactionHash.hex()

def _base_tx(account, value=0):
    return {
        "from": account.address,
        "nonce": w3.eth.get_transaction_count(account.address),
        "gas": 1_200_000,
        "gasPrice": w3.to_wei("20", "gwei"),
        "value": value,
        "chainId": CHAIN_ID
    }

# ---- Flask app ----
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.post("/mint")
def mint():
    token_uri = request.form.get("token_uri")
    tx = c_nft.functions.safeMint(acct_seller.address, token_uri).build_transaction(
        _base_tx(acct_seller)
    )
    txh = _build_and_send_tx(acct_seller, tx)
    return render_template("index.html", mint_tx=txh)

@app.post("/approve")
def approve():
    token_id = int(request.form.get("token_id"))
    tx = c_nft.functions.approve(ADDR_MARKET, token_id).build_transaction(
        _base_tx(acct_seller)
    )
    txh = _build_and_send_tx(acct_seller, tx)
    return render_template("index.html", approve_tx=txh)

@app.post("/list")
def list_for_sale():
    token_id = int(request.form.get("token_id"))
    price_eth = request.form.get("price_eth")
    price_wei = w3.to_wei(Decimal(price_eth), 'ether')
    tx = c_mk.functions.list(ADDR_MY_NFT, token_id, price_wei).build_transaction(
        _base_tx(acct_seller)
    )
    txh = _build_and_send_tx(acct_seller, tx)
    return render_template("index.html", list_tx=txh)

@app.post("/buy")
def buy():
    token_id = int(request.form.get("token_id"))
    price_eth = request.form.get("price_eth")
    price_wei = w3.to_wei(Decimal(price_eth), 'ether')
    tx = c_mk.functions.buy(ADDR_MY_NFT, token_id).build_transaction(
        _base_tx(acct_buyer, value=price_wei)
    )
    txh = _build_and_send_tx(acct_buyer, tx)
    return render_template("index.html", buy_tx=txh)

@app.get("/query")
def query():
    token_id = int(request.args.get("token_id"))
    try:
        (nft, tid, seller, price, active) = c_mk.functions.getListing(ADDR_MY_NFT, token_id).call()
        q = {
            'nft': nft,
            'tokenId': tid,
            'seller': seller,
            'priceWei': str(price),
            'priceETH': str(w3.from_wei(price, 'ether')),
            'active': active
        }
        return render_template("index.html", query=json.dumps(q, indent=2))
    except Exception as e:
        return render_template("index.html", query=f"Error: {str(e)}")

if __name__ == "__main__":
    app.run(debug=True)
