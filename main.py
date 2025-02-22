import schedule
import time
from web3 import Web3
from datetime import datetime, timedelta
import threading

logo = """
======================================
=       Bot mint NFT  Opensea        =
=          Soneium Chain             =
=        Public Mint Only            =
=          BY :  Indibabi            =
======================================
"""

print(logo)

RPC_URL = "https://rpc.soneium.org"

web3 = Web3(Web3.HTTPProvider(RPC_URL))

if not web3.is_connected():
    raise Exception("Tidak dapat terhubung ke jaringan ")


contract_address = "0x00005EA00Ac477B1030CE78506496e8C2dE24bf5"

contract_abi = [
    {
        "inputs": [
            {"internalType": "address", "name": "nftContract", "type": "address"},
            {"internalType": "address", "name": "feeRecipient", "type": "address"},
            {"internalType": "address", "name": "minterIfNotPayer", "type": "address"},
            {"internalType": "uint256", "name": "quantity", "type": "uint256"}
        ],
        "name": "mintPublic",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    }
]

contract = web3.eth.contract(address=contract_address, abi=contract_abi)
nft_contract = input("Masukkan alamat kontrak NFT: ")
fee_recipient = input("Masukkan alamat Fee: ")
mint_price_input = float(input("Masukkan harga mint (dalam ether): "))
gwei_input = float(input("Masukkan nilai gwei untuk transaksi (contoh: 0.1): "))
quantity_to_mint = int(input("Masukkan jumlah NFT yang ingin di-mint: "))

mint_price = web3.to_wei(mint_price_input, "ether")

def get_private_keys(file_path):
    with open(file_path, 'r') as file:
        keys = file.readlines()
    return [key.strip() for key in keys if key.strip()]

def mint_nft(private_key, quantity=1, fee_recipient=None, minter_if_not_payer=None):
    account = web3.eth.account.from_key(private_key)  
    nonce = web3.eth.get_transaction_count(account.address)
    
    fee_recipient = fee_recipient or "0x0000a26b00c1F0DF003000390027140000fAa719" 
    minter_if_not_payer = minter_if_not_payer or "0x0000000000000000000000000000000000000000"
    
    tx = contract.functions.mintPublic(
        nft_contract,
        fee_recipient,
        minter_if_not_payer,
        quantity
    ).build_transaction({
        'from': account.address,
        'gas': 300000,
        'gasPrice': web3.to_wei(gwei_input, 'gwei'), 
        'nonce': nonce,
        'chainId': 1868,
        'value': mint_price * quantity 
    })
 
    signed_tx = web3.eth.account.sign_transaction(tx, private_key)
    
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
    print(f"Transaction hash for wallet {account.address}: {web3.to_hex(tx_hash)}")
    
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    
    if receipt.status == 1:
        print(f"Minting successful for wallet: {account.address}")
    else:
        print(f"Minting failed for wallet: {account.address}")

def mint_nft_scheduled():
    private_keys = get_private_keys('pk.txt')
    threads = []

    for pk in private_keys:
        thread = threading.Thread(target=mint_nft, args=(pk, quantity_to_mint))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

print("Pilih opsi:")
print("1. Mint sekarang")
print("2. Jadwalkan mint")

choice = input("Masukkan pilihan Anda (1/2): ")

if choice == "1":
    print("Memulai proses minting sekarang...")
    mint_nft_scheduled()

elif choice == "2":
    jam_input = input("Masukkan jam (format 24 jam, contoh: 04): ")
    menit_input = input("Masukkan menit (contoh: 00): ")
    schedule_time = f"{jam_input}:{menit_input}"
    schedule.every().day.at(schedule_time).do(mint_nft_scheduled)

    print(f"Bot akan berjalan pada jam {schedule_time} WIB...")

    while True:
        schedule.run_pending()
        time.sleep(1)

else:
    print("Pilihan tidak valid. Silakan coba lagi.")  
