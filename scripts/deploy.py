from brownie import network, config, Box, ERC1967Proxy, Contract, BoxV2
from scripts.helpful_scripts import get_account, upgrade, encode_function_data


def main():
    account = get_account()
    box = Box.deploy({"from": account})
    print(f"Box deployed at {box.address}")
    # creating encoded data to initialize contract
    box_encoded_initializer_function = encode_function_data(box.initialize, 1, account)
    proxy = ERC1967Proxy.deploy(
        box.address,
        box_encoded_initializer_function,
        {"from": account, "gas_limit": 1000000}
        # added gas limit to be safe sometimes proxy have hasrd time figuring out gas
    )
    print(f"Proxy deployed to {proxy}, you can now upgrade to v2!")
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    # being a proxy it will delegate all funciton to implentaton(box) contract
    print(f"Value : {proxy_box.retrieve()}")
    tx_store = proxy_box.store(2, {"from": account})
    tx_store.wait(1)
    print(f"New Value : {proxy_box.retrieve()}")
    print(account)
    # upgrading to box_v2
    # 1. Deploying BoxV2
    boxv2 = BoxV2.deploy({"from": account})
    print(f"BoxV2 deployed at {box.address}")
    # 2. upgrading the implementatino
    tx_up = proxy_box.upgradeTo(boxv2.address, {"from": account})
    tx_up.wait(1)
    print("proxy has been upgraded!")
    # 3. creating on object of proxy which delegates to boxv2
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    # this will return 2 as variables are stored on proxy contract instead of implementaion
    print(f"Value : {proxy_box.retrieve()}")
    tx_store = proxy_box.increment({"from": account})
    print(f"New Value : {proxy_box.retrieve()}")
    tx_store.wait(1)
