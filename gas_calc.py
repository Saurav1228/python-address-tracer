import requests
from web3 import Web3

# Replace with your Alchemy API key
ALCHEMY_API_KEY = ''

# The address to check
ADDRESS = ''

# Alchemy API URL
ALCHEMY_URL = f"https://eth-mainnet.alchemyapi.io/v2/{ALCHEMY_API_KEY}"

# Initialize a Web3 instance
w3 = Web3(Web3.HTTPProvider(ALCHEMY_URL))

def get_transactions(address):
    url = f"{ALCHEMY_URL}/getAssetTransfers"
    payload = {
        "fromBlock": "0x0",
        "toBlock": "latest",
        "fromAddress": address,
        "category": ["external", "internal", "erc20", "erc721", "erc1155"],
        "withMetadata": True,
        "excludeZeroValue": True,
        "maxCount": "0x3e8"  # 1000 in hex
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()['result']

def calculate_gas_fees(transactions):
    total_gas_fees = 0
    for tx in transactions:
        if 'gasUsed' in tx and 'effectiveGasPrice' in tx:
            gas_used = int(tx['gasUsed'], 16)
            gas_price = int(tx['effectiveGasPrice'], 16)
            total_gas_fees += gas_used * gas_price
    return total_gas_fees

def main():
    transactions = get_transactions(ADDRESS)
    total_gas_fees = calculate_gas_fees(transactions)
    total_gas_fees_eth = w3.fromWei(total_gas_fees, 'ether')
    print(f"Total gas fees spent by {ADDRESS}: {total_gas_fees_eth} ETH")

if __name__ == "__main__":
    main()
