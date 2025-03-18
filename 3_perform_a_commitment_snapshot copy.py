import concurrent.futures
from constants import algorand, get_app_client, address, signer
from snapshot_petition_client import AccountSet, AccumulateWeightForSnapshotRoundArgs
from algosdk.encoding import encode_address

snapshot_petition_app_client = get_app_client(address, signer)

all_boxes = algorand.app.get_box_names(snapshot_petition_app_client.app_id)
all_petition_signers = []

for box in all_boxes:
    box_name = box.name_raw
    if box_name[0] != list(b'P')[0]:
        petitioner = encode_address(box_name)
        all_petition_signers.append(petitioner)

# Split all petition signers into groups of 4 (Max account reference allowance)
split_petition_signers = [AccountSet(all_petition_signers[i:i+4]) for i in range(0, len(all_petition_signers), 4)]

def send_snapshot_request(signers, set_snapshot=False):
    new_group = snapshot_petition_app_client.new_group()
    if set_snapshot:
        new_group.set_snapshot_round()
    new_group.accumulate_weight_for_snapshot_round(
        args=AccumulateWeightForSnapshotRoundArgs(
            accounts=signers
        ),
    )
    print("Sending snapshot request . . .")
    new_group.send(
        send_params={
            'populate_app_call_resources': True
        }
    )
    print("Request submitted")

# Threading as there is no current new_group.submit() method (to my knowledge), only new_group.send() which is not asynchronous
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = []
    # First group should call set_snapshot_round(), others do not.
    for i, signers in enumerate(split_petition_signers):
        is_first_group = (i == 0)
        future = executor.submit(send_snapshot_request, signers, is_first_group)
        futures.append(future)

print("All votes counted if none of these transactions failed and all groups are successfully submitted within round")
