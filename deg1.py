import requests
import time

def check_eth_transfer(address1, address2, api_key, max_retries=5, retry_delay=1):
    url = f"https://eth-mainnet.g.alchemy.com/v2/{api_key}"
    
    query1 = {
        "jsonrpc": "2.0",
        "method": "alchemy_getAssetTransfers",
        "params": [
            {
                "fromBlock": "0x0",
                "toBlock": "latest",
                "fromAddress": address1,
                "toAddress": address2,
                "category": ["external", "internal", "erc20", "erc721", "erc1155", "specialnft"]
            }
        ],
        "id": 1
    }
    
    query2 = {
        "jsonrpc": "2.0",
        "method": "alchemy_getAssetTransfers",
        "params": [
            {
                "fromBlock": "0x0",
                "toBlock": "latest",
                "fromAddress": address2,
                "toAddress": address1,
                "category": ["external", "internal", "erc20", "erc721", "erc1155", "specialnft"]
            }
        ],
        "id": 1
    }

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
                    if "rate limits" in data["error"]["message"].lower():
                        time.sleep(retry_delay * (2 ** attempt))
                        continue
                break
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
                time.sleep(retry_delay * (2 ** attempt))
        return None

    transfers1 = fetch_transfers(query1)
    if transfers1:
        return transfers1[0]["hash"]

    transfers2 = fetch_transfers(query2)
    if transfers2:
        return transfers2[0]["hash"]

    return None

address1 = " "
address2 = " "
api_key = " "

tx_hash = check_eth_transfer(address1, address2, api_key)
if tx_hash:
    print(f"The two addresses have sent ETH to each other directly. First transaction hash: {tx_hash}")
else:
    print("No direct ETH transfers found between the two addresses.")
