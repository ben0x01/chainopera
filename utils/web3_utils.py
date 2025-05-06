from datetime import datetime, timezone


def create_sign_message(wallet_address:str, nonce: str) -> str:
    now = datetime.now(timezone.utc)
    iso_now = now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    message = (
        f"https://chainopera.ai wants you to sign in with your Ethereum account:\n{wallet_address}\n\nSign in with Ethereum\n\nURI: https://chainopera.ai\nVersion: 1\nChain ID: 1\nNonce: {nonce}\nIssued At: {iso_now}"
    )

    return message