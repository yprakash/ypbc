import asyncio
import json
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('main')
load_dotenv()

from utils.w3_utils import w3, get_contract, get_contract_address

UNI_POOLS_FILE_NAME = 'config/uniswapv3_pools.json'


def get_uniswap_v3_pool_address(token1, token2, fee=3000, raise_error=True):
    pool = token1 + '/' + token2 + '-' + str(fee)
    try:
        tokenA = w3.to_checksum_address(get_contract_address(token1))
        tokenB = w3.to_checksum_address(get_contract_address(token2))
        factory_contract = get_contract('Uniswap V3: Factory')
        pool_address = factory_contract.functions.getPool(tokenA, tokenB, fee).call()
        if int(pool_address, 16) == 0:
            logger.error(f'Pool not found for {pool}')
            return None
        logger.info(f'Found pool for {pool}: {pool_address}')
        return pool_address
    except Exception as e:
        logger.error(f"Error getting pool info for {pool}: {e}")
        if raise_error:
            raise e
        return None

def get_all_user_pool_addresses(file1=UNI_POOLS_FILE_NAME):
    uni_pools = []
    with open(file1) as f1:
        pools_list = json.load(f1)

    for token1, token2, fees in pools_list:
        for fee in fees:
            pool_address = get_uniswap_v3_pool_address(token1, token2, fee)
            if pool_address:
                uni_pools.append(pool_address)
    return uni_pools

async def add_user(user):
    logger.info(f'Adding user {user}')
    uni_pools = get_all_user_pool_addresses()
    logger.info(f'Found {len(uni_pools)} pools for {user}: {uni_pools}')

async def main():
    logger.info('Getting all Uniswap V3 pool addresses')
    users = ['user1']
    user_tasks = [asyncio.create_task(add_user(user)) for user in users]
    await asyncio.gather(*user_tasks)  # Run all listeners concurrently

if __name__ == '__main__':
    asyncio.run(main())
