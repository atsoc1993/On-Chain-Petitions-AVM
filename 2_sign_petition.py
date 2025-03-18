from constants import algorand, get_app_client, address, signer
from algokit_utils import PaymentParams, AlgoAmount, CommonAppCallParams
from snapshot_petition_client import SignPetitionArgs


#Use a different address and signer to sign petition as someone else
snapshot_petition_app_client = get_app_client(address, signer)

mbr_payment = algorand.create_transaction.payment(
    PaymentParams(
        sender=address,
        signer=signer,
        receiver=snapshot_petition_app_client.app_address,
        amount=AlgoAmount(algo=0.02),
    )
)

txn_response = snapshot_petition_app_client.send.sign_petition(
    args=SignPetitionArgs(
        mbr_payment=mbr_payment,
    ),
    params=CommonAppCallParams(
        max_fee=AlgoAmount(algo=0.01),
    ),
    send_params={
        'populate_app_call_resources': True,
        'cover_app_call_inner_transaction_fees': True
    }
)

print(txn_response.tx_ids)