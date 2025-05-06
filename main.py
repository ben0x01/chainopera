from concurrent.futures import ProcessPoolExecutor
import asyncio
import random
from multiprocessing import Process, Manager
from asyncio import WindowsSelectorEventLoopPolicy

from sqlalchemy.future import select
import time
from db.models.cypher_model import Zk1LabsModel
from src.chainopera_client import ChainOperaClient
from utils.file_utils import read_lines
from utils.request_utils import Impersonate, ImpersonateOs
from utils.broker_utils import TaskExecutor
from config import RANDOM_SLEEP_DELAY, MAX_CONCURRENT_TASKS, DB_PATH
from constants import RPC_URL, EXPLORER_URL
from db.db_client import DatabaseClient, update_db

DB_CLIENT = DatabaseClient(DB_PATH)


def start_process_wallet(wallet, broker, mask_id, code='0'):
    asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    return asyncio.run(process_wallet(wallet, broker, mask_id, code))


async def process_wallet(wallet, broker, mask_id=False, code='0') -> str | None:
    if wallet.login and wallet.join_waiting_list and wallet.follow_twitter and wallet.write_twitter_handle and wallet.discord_oauth and wallet.used_or_received_code != '0':
        return None

    pk = wallet.private_key
    proxy_url = wallet.proxy
    wallet_id = wallet.id
    displayed_id = "***" if mask_id else str(wallet_id)
    os_data = wallet.os_header
    chrome_version = wallet.chrome_version

    if not pk.startswith("0x"):
        pk = "0x" + pk

    if len(pk) != 66:
        raise

    if not proxy_url.startswith("http"):
        proxy_url = "http://" + proxy_url

    os: ImpersonateOs = ImpersonateOs.from_str(os_data)
    version: Impersonate = Impersonate.from_str(chrome_version)

    headers = version.headers(os)

    client = ChainOperaClient(
        rpc_url=RPC_URL,
        private_key=pk,
        explorer_url=EXPLORER_URL,
        proxy_url=proxy_url,
        logger_id=displayed_id,
        retry_attempts=3,
        timeout_429=60,
        headers=headers
    )
    logger = client.logger

    try:
        logger.info(f"Начинаем работу...")

        random_delay = random.uniform(*RANDOM_SLEEP_DELAY)
        await asyncio.sleep(random_delay)

        if not wallet.login:
            resp = await client.login()

            if resp['code'] == 'SUCCESS':
                broker.enqueue_task(update_db, "Zk1Labs",
                                    {"private_key": pk}, {"login": True})
            else:
                raise Exception("An error occurred during login\n{resp}")

            random_delay = random.uniform(*RANDOM_SLEEP_DELAY)
            await asyncio.sleep(random_delay)

        if not wallet.join_waiting_list:
            resp = await client.join_waiting_list(wallet.email)

            if resp['code'] == 'SUCCESS':
                broker.enqueue_task(update_db, "Zk1Labs",
                                    {"private_key": pk}, {"join_waiting_list": True})
            else:
                raise Exception("An error occurred during join_waiting_list\n{resp}")

            random_delay = random.uniform(*RANDOM_SLEEP_DELAY)
            await asyncio.sleep(random_delay)

        if not wallet.follow_twitter:
            resp = await client.follow_twitter()

            if resp['code'] == 'SUCCESS':
                broker.enqueue_task(update_db, "Zk1Labs",
                                    {"private_key": pk}, {"follow_twitter": True})
            else:
                raise Exception("An error occurred during follow_twitter\n{resp}")

            random_delay = random.uniform(*RANDOM_SLEEP_DELAY)
            await asyncio.sleep(random_delay)

        if not wallet.write_twitter_handle:
            resp = await client.write_twitter_handle(wallet.twitter)

            if resp['code'] == 'SUCCESS':
                broker.enqueue_task(update_db, "Zk1Labs",
                                    {"private_key": pk}, {"write_twitter_handle": True})
            else:
                raise Exception("An error occurred during write_twitter_handle\n{resp}")

            random_delay = random.uniform(*RANDOM_SLEEP_DELAY)
            await asyncio.sleep(random_delay)

        if not wallet.discord_oauth:
            resp = await client.discord_oauth(wallet.ds_token)

            if resp['code'] == 'SUCCESS':
                broker.enqueue_task(update_db, "Zk1Labs",
                                    {"private_key": pk}, {"discord_oauth": True})
            else:
                raise Exception("An error occurred during discord_oauth\n{resp}")

        if code != '0':
            time.sleep(random.uniform(*[1200, 1800]))

        if not wallet.used_code and wallet.used_or_received_code == "0":
            if code == '0':
                while True:
                    random_delay = random.uniform(*RANDOM_SLEEP_DELAY)
                    await asyncio.sleep(random_delay)
                    code = await client.get_invite_code()

                    if code != '':
                        break

                broker.enqueue_task(update_db, "Zk1Labs",
                                    {"private_key": pk}, {"used_code": False})
                broker.enqueue_task(update_db, "Zk1Labs",
                                    {"private_key": pk}, {"used_or_received_code": code})
            else:
                resp = await client.write_invite_code(code)
                while True:
                    if resp['code'] == 'SUCCESS':
                        break
                    elif resp['code'] == "" or resp['code'] is None or resp['code'] == "FAILURE":
                        logger.info(f"Waiting for task confirmation\n{resp}\n{code}")
                        time.sleep(random.uniform(*[300, 900]))

                broker.enqueue_task(update_db, "Zk1Labs",
                                    {"private_key": pk}, {"used_code": True})

                broker.enqueue_task(update_db, "Zk1Labs",
                                    {"private_key": pk}, {"used_or_received_code": code})

        logger.info(f"Все задачи завершены.\n")

        return code
    except Exception as e:
        logger.error(f"Общая ошибка: {e}")
        return None


async def main():
    print("Выберите действие:")
    print("1: Заполнить данные в базу")
    print("2: Запустить активности (показывать ID)")
    print("3: Запустить активности (скрыть ID)")

    choice = input("Введите номер действия: ")

    if choice == "1":
        await DB_CLIENT.init_db()

        private_keys = read_lines("./data/private_keys.txt")
        proxies = read_lines("./data/proxies.txt")
        emails = read_lines("./data/email.txt")
        twitters = read_lines("./data/twitter.txt")
        ds_tokens = read_lines("./data/discord_tokens.txt")

        if len(private_keys) != len(proxies):
            return

        async with DB_CLIENT.get_session() as session:
            for pk, proxy, email, twitter, ds_token in zip(private_keys, proxies, emails, twitters, ds_tokens):
                await DB_CLIENT.add_account(Zk1LabsModel, pk, proxy, email, twitter, ds_token, session)
    elif choice in ("2", "3"):
        try:
            await DB_CLIENT.init_db()
            mask_id = choice == "3"

            async with DB_CLIENT.get_session() as session:
                rows = await session.execute(select(Zk1LabsModel))
                wallets = rows.scalars().all()

            total_accounts = len(wallets)

            if total_accounts % 11 != 0:
                print("Количество аккаунтов не кратно 11!")
                raise

            manager = Manager()
            shared_queue = manager.Queue()
            broker = TaskExecutor(shared_queue)
            process = Process(target=broker.run_async_tasks)
            process.start()

            with ProcessPoolExecutor(max_workers=MAX_CONCURRENT_TASKS) as executor:
                first_group_size = total_accounts // 11
                first_group = wallets[:first_group_size]
                codes = []

                wallet_index = 0
                futures = [executor.submit(start_process_wallet, wallet, broker, mask_id) for wallet in first_group]
                for future in futures:
                    code = future.result()
                    if wallets[wallet_index].used_or_received_code == '0':
                        codes.append(code)
                    else:
                        codes.append(wallets[wallet_index].used_or_received_code)
                    wallet_index += 1

                remaining_wallets = wallets[first_group_size:]
                code_index = 0
                processed_accounts = 0

                tasks = []
                for wallet in remaining_wallets:
                    current_code = codes[code_index % len(codes)]
                    tasks.append((start_process_wallet, (wallet, broker, mask_id, current_code)))
                    processed_accounts += 1
                    if processed_accounts >= 10:
                        code_index += 1
                        processed_accounts = 0

                for i in range(0, len(remaining_wallets), MAX_CONCURRENT_TASKS):
                    chunk = tasks[i:i + (
                        MAX_CONCURRENT_TASKS if i + MAX_CONCURRENT_TASKS < len(remaining_wallets) else len(
                            remaining_wallets))]

                    futures = [executor.submit(task[0], *task[1]) for task in chunk]
                    for future in futures:
                        future.result()

            broker.close(process)
            print("Все процессы завершены")
        except Exception as e:
            raise e


if __name__ == "__main__":
    asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
