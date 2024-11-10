from algosdk import mnemonic, account, transaction
from algosdk.account import address_from_private_key
from algosdk.v2client import algod
import time
import random
import ssl
import traceback


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
}

# Hardcoded Stokvel group with 5 members
hardcoded_stokvel_group = {
    "name": "Community Stokvel",
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

def contribute_to_stokvelsim(algod_client, private_key, address, stokvel,amount):
    try:
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
    print(f"\nStokvel '{stokvel['name']}' Status:")
    print(" - Members and their Contributions:")
    for member, contribution in stokvel["contributions"].items():
        print(f"   {member}: {contribution} Algos")


# Transfer funds between two members
def transfer_funds(algod_client, private_key, from_address, to_address, amount):
    try:
        amount_micro = amount * 1e6  # Convert Algos to microAlgos
        params = algod_client.suggested_params()
        unsigned_txn = transaction.PaymentTxn(from_address, params, to_address, int(amount_micro))
        signed_txn = unsigned_txn.sign(private_key)
        tx_id = algod_client.send_transaction(signed_txn)
        wait_for_confirmation(algod_client, tx_id)
        print(f"Transferred {amount} Algos from {from_address} to {to_address}.")
    except Exception as e:
        print(f"Error during fund transfer: {e}")

#payout from stokvel
def payout_from_stokvel(algod_client, stokvel,Multisig):
    try:
        print(f"Payout from Stokvel '{stokvel['name']}' initiated.")

        # Amount to be paid out (e.g., 1 Algo)
        payout_amount = 1000000  # 1 Algo = 1,000,000 microAlgos

        # Collect authorizations from members
        authorized_members = 0
        authorized_addresses = []  # Store authorized member addresses

        for member in stokvel["members"]:
            authorization = input(f"Authorize payout for {member} (y/n): ").strip().lower()
            if authorization == 'y':
                authorized_addresses.append(member)
                authorized_members += 1
            if authorized_members >= 4:
                print("Sufficient authorizations received. Proceeding with the payout.")
                break
        else:
            print("Error: Not enough authorizations. At least 4 members must approve the payout.")
            return

        # Use the existing multisig account for the payout transaction
        msig_account_address = "4GK46635MKFBCOPAY2BFC5MDOVRDLQ6YFJ2VAI5GOPWSBNHIMDGCP3E6XY"  # This is just the address
        sp = algod_client.suggested_params()

        # Create the payment transaction
        msig_pay = transaction.PaymentTxn(
            msig_account_address,  # Use the address directly
            sp,
            authorized_addresses[0],  # For demonstration, send to the first authorized member
            payout_amount,
            close_remainder_to=authorized_addresses[0]  # Optionally close remainder to the first address
        )


        # Wrap the payment transaction inside the multisig transaction
        msig_txn = transaction.MultisigTransaction(msig_pay,Multisig)

        # Sign the transaction with the authorized signers of the Stokvel account
        for account in hardcoded_accounts:
            private_key = mnemonic.to_private_key(account["mnemonic"])
            msig_txn.sign(private_key)

        # Send the transaction
        txid = algod_client.send_transaction(msig_txn)

        # Wait for the transaction to be confirmed
        result = transaction.wait_for_confirmation(algod_client, txid, 4)
        print(f"Payout made from Stokvel account confirmed in round {result['confirmed-round']}")

    except Exception as e:
        print(f"Error during payout: {e}")

def get_mnemonic_by_address(address, accounts_list):
    """Helper function to get mnemonic from hardcoded_accounts list"""
    for account in accounts_list:
        if account["address"] == address:
            return account["mnemonic"]
    return None


def simulate_stokvel_cycle(algod_client, multisig, stokvel_group):
    try:
        print(f"Simulating 5-month cycle.")

        # Get stokvel members from the group
        stokvel_members = stokvel_group["members"]
        print(f"stokvel_members: {stokvel_members}")

        # Simulate the cycle for 5 months
        for month in range(1, 6):
            print(f"\n--- Month {month} ---")

            # Step 1: All members contribute their monthly deposit
            deposit_amount = 1 * 1000000  # 1 Algo in microAlgos
            for member_address in stokvel_members:
                try:
                    print(f"Processing deposit for member: {member_address}")

                    # Get mnemonic from the global hardcoded_accounts list
                    mnemonic_phrase = get_mnemonic_by_address(member_address, hardcoded_accounts)

                    if mnemonic_phrase:
                        # Correctly use mnemonic.to_private_key as a function
                        private_key = mnemonic.to_private_key(mnemonic_phrase)
                        contribute_to_stokvelsim(
                            algod_client,
                            private_key,
                            member_address,
                            stokvel_group,
                            deposit_amount
                        )
                        print(f"Member {member_address} deposited 1 Algo.")
                    else:
                        print(f"Could not find mnemonic for member {member_address}")

                except Exception as e:
                    print(f"Error processing deposit for {member_address}: {e}")
                    traceback.print_exc()  # Added to show full error trace
                    continue

            # Step 2: Select member for this month's payout
            selected_member = stokvel_members[month - 1]  # Sequential selection
            payout_amount = int(0.60 * deposit_amount * 5)  # 60% of total deposits
            print(f"\nSelected member for payout: {selected_member}")
            print(f"Payout amount: {payout_amount / 1000000} Algos")

            # Step 3: Collect authorizations
            authorized_members = 0
            authorized_addresses = []

            for member in stokvel_members:
                authorization = input(f"Authorize payout to {selected_member}? (y/n): ").strip().lower()
                if authorization == 'y':
                    authorized_addresses.append(member)
                    authorized_members += 1
                if authorized_members >= 4:
                    print("Sufficient authorizations received. Proceeding with payout.")
                    break

            if authorized_members < 4:
                print("Not enough authorizations received. Skipping payout.")
                continue

            # Step 4: Process payout
            try:
                msig_account_address = multisig.address()
                sp = algod_client.suggested_params()

                # Create and sign multisig transaction
                msig_pay = transaction.PaymentTxn(
                    msig_account_address,
                    sp,
                    selected_member,
                    payout_amount
                )

                msig_txn = transaction.MultisigTransaction(msig_pay, multisig)

                # Sign with authorized members
                for auth_address in authorized_addresses[:4]:  # Use first 4 authorizations
                    member_mnemonic = get_mnemonic_by_address(auth_address, hardcoded_accounts)
                    if member_mnemonic:
                        private_key = mnemonic.to_private_key(member_mnemonic)
                        msig_txn.sign(private_key)

                # Send transaction
                txid = algod_client.send_transaction(msig_txn)
                wait_for_confirmation(algod_client, txid)
                print(f"Payout of {payout_amount / 1000000} Algos to {selected_member} confirmed.")

            except Exception as e:
                print(f"Error processing payout: {e}")
                traceback.print_exc()  # Added to show full error trace
                continue

            print(f"End of Month {month} completed.")

        print("\n5-month cycle completed successfully.")

    except Exception as e:
        print(f"Critical error in simulation: {e}")
        traceback.print_exc()
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
        if choice == "1":
            private_key, address = generate_new_account()
        elif choice == "2":
            private_key = mnemonic.to_private_key(hardcoded_accounts[0]["mnemonic"])
            address = hardcoded_accounts[0]["address"]
            multisig_accounts = [
                "4MMK35CO2ISYD4TPY5ZRUWNDUJ3MXCIM6AVGNNEBZWD2VCZM4E4JVX2CF4",
                "YRQFF5PSX2HS6PZ75TWAISFST2XROUVYUQRPK5ZXU7SNN7QWGTBPFJXSSQ",
                "VI7NU5WFYUPOKPSC3RGY7OZNWK3YHSZF4D5Y3S2XBCLJG5UY6Y4K3D2PU4",
                "VKAWCU7XS2WG7KU5N2XAR5UU5SQGJUGIBMUQ25KYW6K4WMCRQQAUPGA3VU",
                "BMSL2ZRZJ2DXNSVKDZITFRUFNOO24BIQHV2DDVI7SM3UW5B5RQH3KQZ7NI"
            ]
            msig = transaction.Multisig(1, 4, multisig_accounts)
            hardcoded_stokvel_account["address"] = msig.address()
            print("Multisig Address: ", msig.address())
            print(f"Using hardcoded account: {address}")
        else:
            print("Invalid choice, please try again.")

    # Stokvel system menu
    while True:
        print("\n--- Stokvel Management ---")
        print("1. Contribute to Stokvel")
        print("2. View Stokvel Status")
        print("3. Transfer Funds")
        print("4. Payout from Stokvel")
        print("5. Simulate Payout from Stokvel for 5 months")
        print("6. Exit")
        option = input("Select an option: ").strip()
        if option == "1":
            contribute_to_stokvel(algod_client, private_key, address, hardcoded_stokvel_group)
        elif option == "2":
            view_stokvel_status(hardcoded_stokvel_group)
        elif option == "3":
            to_address = input("Enter recipient address: ").strip()
            amount = float(input("Enter amount to transfer: ").strip())
            transfer_funds(algod_client, private_key, address, to_address, amount)
        elif option == "4":
            payout_from_stokvel(algod_client, hardcoded_stokvel_group,msig)
        elif option == "5":
            simulate_stokvel_cycle(algod_client, msig, hardcoded_stokvel_group)
        elif option == "6":
            break
        else:
            print("Invalid option, please try again.")


if __name__ == "__main__":
    main()
