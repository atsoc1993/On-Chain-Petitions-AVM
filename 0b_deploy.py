from constants import snapshot_petition_factory, algorand, address, signer
from algokit_utils import PaymentParams, AlgoAmount
from dotenv import load_dotenv, set_key

load_dotenv()

print("Deploying contract . . .")
snapshot_petition_client, response = snapshot_petition_factory.send.bare.create()

print("Funding App MBR of 0.1A to be an active account")
mbr_payment = algorand.send.payment(
    PaymentParams(
        sender=address,
        signer=signer,
        amount=AlgoAmount(algo=0.1),
        receiver=snapshot_petition_client.app_address
    )
)
set_key('.env', 'app_id', str(snapshot_petition_client.app_id))
print("Funded App, set App ID key in .env")
