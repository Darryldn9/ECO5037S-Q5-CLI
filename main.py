from algosdk import mnemonic, account, transaction
from algosdk.v2client import algod
import time
import ssl

# Create an Algod client
# Create an Algod client
def create_algod_client():
    algod_address = "https://testnet-api.algonode.cloud"
    algod_token = ""
    algod_client = algod.AlgodClient(algod_token, algod_address)  # Removed ssl_context
    return algod_client


# Hardcoded accounts (with provided mnemonics)
hardcoded_accounts = [
    {
        "mnemonic": "history tuna elbow response glass ribbon sing leisure discover fold warrior arrow hurt grid gravity garden lizard impulse tired divorce bulk flower skill able joke",
        "address": "4MMK35CO2ISYD4TPY5ZRUWNDUJ3MXCIM6AVGNNEBZWD2VCZM4E4JVX2CF4"
    },
    {
        "mnemonic": "know option trigger viable cart install lawn indicate lemon steel job heart alley prosper stamp left above wool shrimp punch ginger walnut angry abstract bright",
        "address": "YRQFF5PSX2HS6PZ75TWAISFST2XROUVYUQRPK5ZXU7SNN7QWGTBPFJXSSQ"
    },
    {
        "mnemonic": "prepare news spider fuel require harbor december inside melody drum daring bitter mad twin rail scissors clog oven grit above unknown garden unknown abstract arctic",
        "address": "VI7NU5WFYUPOKPSC3RGY7OZNWK3YHSZF4D5Y3S2XBCLJG5UY6Y4K3D2PU4"
    },
    {
        "mnemonic": "february hat menu fee birth grab rich name hood solid eyebrow narrow figure sniff race midnight apart enforce electric exhaust ecology coyote spatial above garbage",
        "address": "VKAWCU7XS2WG7KU5N2XAR5UU5SQGJUGIBMUQ25KYW6K4WMCRQQAUPGA3VU"
    },
    {
        "mnemonic": "river great eyebrow true disagree obtain credit time tackle unknown stadium wall hood cabbage liquid dilemma reward dish hurt opinion rain simple picture absorb today",
        "address": "BMSL2ZRZJ2DXNSVKDZITFRUFNOO24BIQHV2DDVI7SM3UW5B5RQH3KQZ7NI"
    }
]

# Hardcoded Stokvel account
hardcoded_stokvel_account = {
    "address": "CGOFMXFPAE4KGJ6OMMPPFN2WFFFTVOZAR456FU4Y3NUXA4LTEOFUCV7U2A",
    "mnemonic": "eternal sadness coral render odor hen brand occur hundred bottom trouble jaguar brass uncle mistake whip bitter loan raise dumb weapon vintage have absorb spell"
}

# Hardcoded Stokvel group with 5 members
hardcoded_stokvel_group = {
    "name": "Community Stokvel",
    "goal": 1000.0,  # Goal in Algos
    "members": [
        hardcoded_accounts[0]["address"],
        hardcoded_accounts[1]["address"],
        hardcoded_accounts[2]["address"],
        hardcoded_accounts[3]["address"],
        hardcoded_accounts[4]["address"]
    ],
    "contributions": {
        hardcoded_accounts[0]["address"]: 0.0,
        hardcoded_accounts[1]["address"]: 0.0,
        hardcoded_accounts[2]["address"]: 0.0,
        hardcoded_accounts[3]["address"]: 0.0,
        hardcoded_accounts[4]["address"]: 0.0
    }
}

# Create a new Algorand account
def generate_new_account():
    private_key, address = account.generate_account()
    mnemonic_phrase = mnemonic.from_private_key(private_key)
    print(f"New Account Created\nAddress: {address}\nMnemonic: {mnemonic_phrase}")
    return private_key, address

# Contribute to Stokvel
def contribute_to_stokvel(algod_client, private_key, address, stokvel):
    try:
        amount = float(input(f"Enter contribution amount to '{stokvel['name']}' (in Algos): ").strip()) * 1e6
        receiver_address = hardcoded_stokvel_account["address"]  # Contributions go to Stokvel group account
        params = algod_client.suggested_params()
        unsigned_txn = transaction.PaymentTxn(address, params, receiver_address, int(amount))
        signed_txn = unsigned_txn.sign(private_key)
        tx_id = algod_client.send_transaction(signed_txn)
        wait_for_confirmation(algod_client, tx_id)

        # Update contributions in Stokvel
        stokvel["contributions"][address] = stokvel["contributions"].get(address, 0) + amount / 1e6
        print(f"Contribution successful! {amount / 1e6} Algos added to Stokvel '{stokvel['name']}'.")
    except Exception as e:
        print(f"Error during contribution: {e}")

# View Stokvel status
def view_stokvel_status(stokvel):
    total_contributions = sum(stokvel["contributions"].values())
    print(f"\nStokvel '{stokvel['name']}' Status:")
    print(f" - Goal: {stokvel['goal']} Algos")
    print(f" - Total Contributions: {total_contributions} Algos")
    print(" - Members and their Contributions:")
    for member, contribution in stokvel["contributions"].items():
        print(f"   {member}: {contribution} Algos")
    if total_contributions >= stokvel["goal"]:
        print("Goal achieved! Ready for payout.")

# Wait for transaction confirmation
def wait_for_confirmation(client, txid, timeout=10):
    start_time = time.time()
    while True:
        try:
            status = client.pending_transaction_info(txid)
            if status.get("confirmed-round") and status["confirmed-round"] > 0:
                print(f"Transaction confirmed in round {status['confirmed-round']}.")
                return
        except Exception as e:
            print(f"Error checking transaction status: {e}")

        if time.time() - start_time > timeout:
            raise Exception("Transaction confirmation timeout.")
        time.sleep(1)

# Main menu
def main():
    algod_client = create_algod_client()

    # Account setup
    private_key, address = None, None
    while not private_key or not address:
        print("\n--- Account Setup ---")
        print("1. Generate a new account")
        print("2. Use a hardcoded account")
        choice = input("Select an option (1 or 2): ").strip()
        if choice == '1':
            private_key, address = generate_new_account()
        elif choice == '2':
            for idx, acc in enumerate(hardcoded_accounts):
                print(f"{idx + 1}. Address: {acc['address']}")
            selected = int(input("Select an account: ")) - 1
            private_key = mnemonic.to_private_key(hardcoded_accounts[selected]["mnemonic"])
            address = hardcoded_accounts[selected]["address"]
        else:
            print("Invalid choice. Please select 1 or 2.")

    # Main menu
    while True:
        print("\n--- Stokvel Main Menu ---")
        print("1. Create Stokvel group")
        print("2. Contribute to a Stokvel group")
        print("3. View Stokvel group status")
        print("4. Payout from Stokvel")
        print("5. Exit")
        option = input("Select an option (1-5): ").strip()

        if option == '1':
            print("Stokvel group already created.")
        elif option == '2':
            print("Contribute to the Stokvel group (address):", hardcoded_stokvel_account['address'])
            contribute_to_stokvel(algod_client, private_key, address, hardcoded_stokvel_group)
        elif option == '3':
            print("Stokvel group (address):", hardcoded_stokvel_account['address'])
            view_stokvel_status(hardcoded_stokvel_group)
        elif option == '4':
            print("Payout functionality not implemented.")
        elif option == '5':
            print("Exiting...")
            break
        else:
            print("Invalid option. Please select a number between 1 and 5.")

if __name__ == "__main__":
    main()
