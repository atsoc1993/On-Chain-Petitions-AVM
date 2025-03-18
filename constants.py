from algokit_utils import AppFactory, AppFactoryParams, AlgorandClient
from algosdk.atomic_transaction_composer import AccountTransactionSigner
from snapshot_petition_client import SnapshotPetitionClient, SourceMap
from algosdk.account import address_from_private_key
from dotenv import load_dotenv, set_key
from pathlib import Path
import json
import os

load_dotenv()

algorand = AlgorandClient.testnet()

pk = os.getenv('pk')
address = address_from_private_key(pk)
signer = AccountTransactionSigner(pk)

pk_2 = os.getenv('pk_2')
address_2 = address_from_private_key(pk_2)
signer_2 = AccountTransactionSigner(pk_2)

pk_3 = os.getenv('pk_3')
address_3 = address_from_private_key(pk_3)
signer_3 = AccountTransactionSigner(pk_3)


snapshot_petition_app_spec = (Path(__file__).parent / 'SnapshotPetition.arc56.json').read_text()
snapshot_petition_app_source_map = SourceMap(json.loads((Path(__file__).parent / 'SnapshotPetition.approval.puya.map').read_text()))

snapshot_petition_factory_params = AppFactoryParams(
    algorand=algorand,
    app_spec=snapshot_petition_app_spec,
    default_sender=address,
    default_signer=signer,
)

snapshot_petition_factory = AppFactory(snapshot_petition_factory_params)

def get_app_client(address, signer):
    if os.getenv('app_id'):
        app_id = int(os.getenv('app_id'))
        snapshot_petition_app_client = algorand.client.get_typed_app_client_by_id(
            typed_client=SnapshotPetitionClient, 
            app_id=app_id, 
            approval_source_map=snapshot_petition_app_source_map,
            default_sender=address,
            default_signer=signer,    
        )

    else:
        print("No App ID in .env, deploy the contract first")
    return snapshot_petition_app_client