from constants import algorand, get_app_client, address, signer
from algokit_utils import PaymentParams, AlgoAmount, CommonAppCallParams
from snapshot_petition_client import SetPetitionDetailsArgs


snapshot_petition_app_client = get_app_client(address, signer)

mbr_payment = algorand.create_transaction.payment(
    PaymentParams(
        sender=address,
        signer=signer,
        receiver=snapshot_petition_app_client.app_address,
        amount=AlgoAmount(algo=1),
    )
)

txn_response = snapshot_petition_app_client.send.set_petition_details(
    args=SetPetitionDetailsArgs(
        petition_details='All future funding MUST go to condiments ONLY',
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