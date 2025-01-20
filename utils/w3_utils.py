import json
import logging
import os

from cachetools import cached, LRUCache
from web3 import Web3

from config.sc_abis import contract_ABIs as SC_ABIS

logger = logging.getLogger(__name__)
logging.getLogger('web3').setLevel(logging.INFO)
logging.getLogger('urllib3').setLevel(logging.INFO)

PROVIDER_URL = os.getenv('PROVIDER_URL')
w3 = Web3(Web3.HTTPProvider(PROVIDER_URL))
if w3.is_connected():
    logger.info(f'Connected to {PROVIDER_URL}')
else:
    s = f'Failed to connect to {PROVIDER_URL}'
    logger.error(s)
    raise ConnectionError(s)

MAX_CACHED_CONTRACTS = 100
SC_FILE_NAME = 'config/smart_contracts.json'
SC_TOKENS_FILE_NAME = 'config/sc_tokens.json'
ADDRESSES = json.load(open(SC_TOKENS_FILE_NAME))
ADDRESSES.update(json.load(open(SC_FILE_NAME)))


def get_web3_instance():
    return w3

def get_contract_address(contract_name, raise_error=True):
    if contract_name not in ADDRESSES:
        e = f'Contract {contract_name} not found in {SC_FILE_NAME} OR {SC_TOKENS_FILE_NAME}'
        if raise_error:
            raise ValueError(e)
        logger.error(e)
        return None
    return ADDRESSES[contract_name]

@cached(cache=LRUCache(maxsize=MAX_CACHED_CONTRACTS))
def get_contract(contract_name, raise_error=True):
    if contract_name not in ADDRESSES:
        e = f'Contract {contract_name} not found in {SC_FILE_NAME} OR {SC_TOKENS_FILE_NAME}'
        if raise_error:
            raise ValueError(e)
        logger.error(e)
        return None

    if contract_name not in SC_ABIS:
        e = f'Contract {contract_name} ABI not found in config/sc_abis.py'
        if raise_error:
            raise ValueError(e)
        logger.error(e)
        return None

    contract = w3.eth.contract(address=ADDRESSES[contract_name], abi=SC_ABIS[contract_name])
    logger.info(f'Loaded contract {contract_name} at address {ADDRESSES[contract_name]}: {contract}')
    return contract
