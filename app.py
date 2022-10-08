from flask import Flask
from flask import request, abort
import requests
from product import Product

import product
from db_session import global_init, create_session

app = Flask(__name__)
from OpenSSL import SSL

context = SSL.Context(SSL.PROTOCOL_TLSv1_2)
context.use_privatekey_file('server.key')
context.use_certificate_file('server.crt')

BASE_URL = "https://hackathon.lsp.team/hk"
API_URL = "/blockchainapi/v1/"
USER_API_URL = ""


@app.route('/blockchainapi/v1/new_wallet')
def create_wallet():
    return requests.post(f'{BASE_URL}/v1/wallets/new').json()


@app.route(f'{API_URL}/transaction/dr', methods=["POST"])
def send_dr():
    data = request.json
    from_user = requests.get(f'{USER_API_URL}/get/{data["uid_from"]}').json()
    dest_user = requests.get(f'{USER_API_URL}/get/{data["uid_dest"]}').json()
    params = {
        "fromPrivateKey": from_user["private_key"],
        "toPublicKey": dest_user["public_key"],
        "amount": data["count"]
    }
    return requests.post(f'{BASE_URL}/v1/transfers/ruble', json=params).json()


@app.route(f'{API_URL}/transaction/matic', methods=["POST"])
def send_matic():
    data = request.json
    from_user = requests.get(f'{USER_API_URL}/get/{data["uid_from"]}').json()
    dest_user = requests.get(f'{USER_API_URL}/get/{data["uid_dest"]}').json()
    if from_user["role"] != "admin":
        return abort(403)
    params = {
        "fromPrivateKey": from_user["private_key"],
        "toPublicKey": dest_user["public_key"],
        "amount": data["count"]
    }
    return requests.post(f'{BASE_URL}/v1/transfers/ruble', json=params).json()


@app.route(f"{API_URL}/nft_collection/<string:uid>")
def nft_collection(uid):
    user = requests.get(f'{USER_API_URL}/get/{uid}').json()
    sesion = create_session()
    balance = requests.get(f'/v1/wallets/{user["public_key"]}/nft/balance').json()
    coll = {"collection": []}
    for i in balance["balance"]:
        if sesion.query(Product).query(Product.token_id in i["tokens"]) is not None:
            elem = i
            elem["for_sale"] = True
            coll["collection"].append(elem)
    return coll


@app.route(f"{API_URL}/transaction/nft")
def send_nft():
    data = request.json
    from_user = requests.get(f'{USER_API_URL}/get/{data["uid_from"]}').json()
    dest_user = requests.get(f'{USER_API_URL}/get/{data["uid_dest"]}').json()
    params = {
        "fromPrivateKey": from_user["private_key"],
        "toPublicKey": dest_user["public_key"],
        "tokenId": data["tokenid"]
    }
    return requests.post(f'{BASE_URL}/v1/transfers/nft', json=params).json()


@app.route(f"{API_URL}/sell_nft")
def sell_nft():
    data = request.json
    session = create_session()
    session.add(Product(seller_id=data["uid_from"], price=data['price'], token_id=data["token_id"]))
    session.commit()
    return {"code": 200}


@app.route(f"{API_URL}/buy_nft")
def sell_nft():
    data = request.json
    session = create_session()
    lot = session.query(Product).filter(Product.token_id == data["tokenid"]).first
    if lot is not None:
        transaction = requests.post(f"{API_URL}/transaction/dr",
                                    json={"uid_from": data["uid_from"], "uid_dest": lot.seller_id,
                                          "count": lot.price}).json()
        status = requests.get(f"{BASE_URL}/v1/transfers/status/{transaction['transactionHash']}").json()
        if status["status"]=="Success":
            transaction = requests.post(f"{API_URL}/transaction/nft",
                                        json={"uid_from": data["uid_from"], "uid_dest": lot.seller_id,
                                              "tokenid": lot.token_id}).json()
            status = requests.get(f"{BASE_URL}/v1/transfers/status/{transaction['transactionHash']}").json()
            if status["status"]=="Success":
                session.delete(lot)
                session.commit()
                return {"code": 200}
            else:
                abort(400)


@app.errorhandler(403)
def acsess_err(err):
    return {
        "code": 403,
        "message": "access denied"
    }


@app.errorhandler(403)
def acsess_err(err):
    return {
        "code": 400,
        "message": "something went wrong"
    }


if __name__ == '__main__':
    global_init("market.sqlite")
    app.run(ssl_context=context)
