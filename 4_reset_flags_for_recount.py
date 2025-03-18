import concurrent.futures
from constants import algorand, get_app_client, address, signer
from snapshot_petition_client import AccountSet, ResetFlagsForRecountArgs
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
split_petition_signers = [
    AccountSet(all_petition_signers[i:i+4])
    for i in range(0, len(all_petition_signers), 4)
]

def reset_flags_for_group(signers):
    new_group = snapshot_petition_app_client.new_group()
    new_group.reset_flags_for_recount(
        args=ResetFlagsForRecountArgs(
            accounts=signers
        )
    )
    print(f"Resetting flags for {signers}")
    new_group.send(
        send_params={
            'populate_app_call_resources': True
        }
    )
    print("Flags reset")

# Use ThreadPoolExecutor to perform the reset calls concurrently
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [executor.submit(reset_flags_for_group, signers) for signers in split_petition_signers]


# NOTE THAT YOU MUST REMOVE THE UTF8 DECODING LINE AND SET TO NONE FOR BOX NAMES AS PER ISSUE OPENED IN ALGOKIT UTILS GITHUB REPO BY ME
# HOLD CONTROL AND CLICK the .get_box_names function above, it should look like this:
'''
    def get_box_names(self, app_id: int) -> list[BoxName]:
        """Get names of all boxes for an application.

        :param app_id: The application ID
        :return: List of box names

        :example:
            >>> app_manager = AppManager(algod_client)
            >>> app_id = 123
            >>> box_names = app_manager.get_box_names(app_id)
        """

        box_result = self._algod.application_boxes(app_id)
        assert isinstance(box_result, dict)
        try:
            name=base64.b64decode(b["name"]).decode("utf-8")
        except:
            name=None
        return [
            BoxName(
                name_raw=base64.b64decode(b["name"]),
                name_base64=b["name"],
                name=name,
            )
            for b in box_result["boxes"]
        ]
'''

