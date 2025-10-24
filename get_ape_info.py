from web3 import Web3
from web3.providers.rpc import HTTPProvider
import requests
import json

bayc_address = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
contract_address = Web3.to_checksum_address(bayc_address)

# You will need the ABI to connect to the contract
# The file 'abi.json' has the ABI for the bored ape contract
# In general, you can get contract ABIs from etherscan
# https://api.etherscan.io/api?module=contract&action=getabi&address=0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D
with open('ape_abi.json', 'r') as f:
    abi = json.load(f)

############################
# Connect to an Ethereum node
api_url = "https://eth-mainnet.g.alchemy.com/v2/6O5ZMvvFpdCfTbTGVrVHB"  # YOU WILL NEED TO PROVIDE THE URL OF AN ETHEREUM NODE
provider = HTTPProvider(api_url)
web3 = Web3(provider)
bayc = web3.eth.contract(address=contract_address, abi=abi)

def get_ape_info(ape_id):
    """
    Return a dict with the current owner, image URI, and eyes trait for a BAYC token.

    Constraints:
    - Only implement this function; do not modify other parts of the file.
    - Input: ape_id (int, 0..9999)
    - Output: {"owner": <address>, "image": <ipfs or https uri>, "eyes": <string>}
    """
    # Keep the template's input validation semantics
    assert isinstance(ape_id, int), f"{ape_id} is not an int"
    assert 0 <= ape_id, f"{ape_id} must be at least 0"
    assert ape_id <= 9999, f"{ape_id} must be less than 10,000"

    # 1) Get the current owner from the BAYC contract
    owner = bayc.functions.ownerOf(ape_id).call()

    # 2) Get the tokenURI (points to metadata on IPFS)
    token_uri = bayc.functions.tokenURI(ape_id).call()

    # 3) Build an HTTP URL to fetch the IPFS JSON (prefer ipfs.io, then Pinata as fallback)
    # Convert ipfs://CID/path to https://<gateway>/ipfs/CID/path
    gateways = ("gateway.pinata.cloud",)
    metadata = {}
    last_err = None
    for gw in gateways:
        if token_uri.startswith("ipfs://"):
            http_url = f"https://{gw}/ipfs/{token_uri[len('ipfs://'):]}"
        else:
            http_url = token_uri  # Already an HTTP(S) URL
        try:
            resp = requests.get(http_url, timeout=20)
            if resp.ok:
                metadata = resp.json()
                break
        except Exception as e:
            last_err = e
            continue
    if not metadata:
        raise RuntimeError(f"Failed to fetch metadata for token {ape_id} from IPFS: {last_err}")

    # 4) Extract image URI (some metadata variants may use 'image_url')
    image_uri = metadata.get("image") or metadata.get("image_url") or ""

    # 5) Extract 'Eyes' trait from attributes
    eyes_value = ""
    attrs = metadata.get("attributes") or []
    if isinstance(attrs, list):
        for a in attrs:
            trait_type = (a.get("trait_type") or a.get("type") or "").strip()
            if trait_type.lower() == "eyes":
                eyes_value = a.get("value", "")
                break

    # 6) Return the required structure
    return {"owner": owner, "image": image_uri, "eyes": eyes_value}
