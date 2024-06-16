import requests
import time
import re

def is_valid_address(address):
    return re.match(r"^0x[a-fA-F0-9]{40}$", address) is not None

def check_eth_transfer(address1, address2, api_key, max_retries=5, retry_delay=1):
    url = f"https://eth-mainnet.g.alchemy.com/v2/{api_key}"
    
    def fetch_transfers(query):
        for attempt in range(max_retries):
            try:
                response = requests.post(url, json=query)
                response.raise_for_status()
                data = response.json()
                if "result" in data and data["result"]["transfers"]:
                    return data["result"]["transfers"]
                elif "error" in data:
                    print(f"API Error: {data['error']['message']}")
                    if "rate limits" in data["error"]["message"].lower() or data["error"]["code"] == -32602:
                        time.sleep(retry_delay * (2 ** attempt))
                        continue
                break
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
                time.sleep(retry_delay * (2 ** attempt))
        return None

    if not is_valid_address(address1) or not is_valid_address(address2):
        print("Invalid Ethereum address.")
        return None
    
    categories = ["external", "internal", "erc20", "erc721", "erc1155", "specialnft"]
    
    def create_query(from_address, to_address):
        params = {
            "fromBlock": "0x0",
            "toBlock": "latest",
            "fromAddress": from_address,
            "category": categories
        }
        if to_address:
            params["toAddress"] = to_address
        return {
            "jsonrpc": "2.0",
            "method": "alchemy_getAssetTransfers",
            "params": [params],
            "id": 1
        }

    query1 = create_query(address1, address2)
    query2 = create_query(address2, address1)

    # Check for degree 1 transfers
    transfers1 = fetch_transfers(query1)
    if transfers1:
        return ("degree 1", transfers1[0]["hash"])
    
    transfers2 = fetch_transfers(query2)
    if transfers2:
        return ("degree 1", transfers2[0]["hash"])

    print("No degree 1 transfers found between the two addresses.")

    # Check for degree 2 transfers
    intermediate_addresses = set()

    query_intermediate = create_query(address1, None)

    transfers_intermediate = fetch_transfers(query_intermediate)
    if transfers_intermediate:
        for transfer in transfers_intermediate:
            intermediate_addresses.add((transfer["to"], transfer["hash"]))

    for intermediate, hash1 in intermediate_addresses:
        if not is_valid_address(intermediate):
            continue
        
        query_degree2 = create_query(intermediate, address2)

        transfers_degree2 = fetch_transfers(query_degree2)
        if transfers_degree2:
            return ("degree 2", hash1, transfers_degree2[0]["hash"])

    print("No degree 2 transfers found between the two addresses.")
    return None

address1 = " "
address2 = " "
api_key = " "

result = check_eth_transfer(address1, address2, api_key)
if result:
    degree = result[0]
    if degree == "degree 1":
        tx_hash = result[1]
        print(f"The two addresses have transferred assets to each other directly. Degree: {degree}, First transaction hash: {tx_hash}")
    elif degree == "degree 2":
        tx_hash1 = result[1]
        tx_hash2 = result[2]
        print(f"The two addresses have transferred assets to each other via an intermediate address. Degree: {degree}, First transaction hash: {tx_hash1}, Second transaction hash: {tx_hash2}")
else:
    print("No direct or degree 2 asset transfers found between the two addresses.")
