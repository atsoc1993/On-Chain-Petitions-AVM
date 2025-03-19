# Overview

This repository contains a POW and source code for an on-chain petition on Algorand. Methods exist currently that set "thresholds" for uniqueness, eg; opted into at least X amount of assets, has a balance of at least Y amount of Algo, has submitted at least Z amount of transactions.
There are many different directions to take with what currently exists in this contract for on-chain petitions, but in its current state (which can easily be reconfigured) sets a threshold for account balance, node activity, and consensus-incentive eligiblity as determining factors for whether or not a signature on a petition is counted.

# Problem
It is difficult to ascertain whether or not an account is unique without requiring KYC.
This becomes even more difficult when attempting to establish uniqueness within a smart contract, especially in situations where a user should not necessarily be required to deposit an amount of an asset with the contract, like to participate in an unexpected petition.

# Solution 
AVM Version 11 makes establishing uniqueness easier, or at least seemingly fairer, as it can also, or exclusively, take consensus participation and/or general node activity as a factor— which most would argue is the most honest/noble method for determining uniqueness.

# Steps
The files have been numbered to assist you in following the workflow, algokit_utils, the py-algorand-sdk, python-dotenv, (algorand-python and algokit as well only if recompiling)
```
pip install algokit_utils
pip install algorand-python
pip install py-algorand-sdk
pip install python-dotenv
```

If you don't have Python installed, visit https://www.python.org/ and make sure to run as administrator and select the "Add Python.exe to Path" option when installing.

## Step 1 (Account Generation):
- Generate accounts via file 0a, ensure they are funded via https://bank.testnet.algorand.network/

## Step 2 (Contract Deployment):
- Deploy the contract via file 0b, the application ID is automatically written into the .env
  *Note: Should you make any changes to the contract do not forget to use `algokit compile py contractFileName.py --output-arc56` and `algokitgen-py -a contractFileName.arc56.json -o contract_client.py`*
  
## Step 3 (Initialize Petition Details):
- Set petition details via file 1_ , currently they are defaulted to 'All future funding MUST go to condiments ONLY'. Petition details cannot be changed once they are set.
![image](https://github.com/user-attachments/assets/9648adc8-54f3-40ad-9617-5cc8bb6e9bd5)

## Step 4 (Gather Signatures):
- Start getting signatures! Petitions can be signed via file 2_, which creates a box for any user with a default "False" boolean flag as the box value, which is set to true during the snapshot process. The contract asserts that a box does not exist for the address already, and will fail if someone attempts to sign the petition twice.
- *Note: Although there is a global counter for signatures obtained, this is not equivalent to the valid signatures count produced after a commitment snapshot, and should only be used for reference. Any arbitrary amount of accounts can sign the petition but does not mean they are valid if the accounts don't meet our uniqueness thresholdings/conditional requirements*
- 
## Step 5 (Perform Commitment Snapshot):
- You can submit snapshot requests to the contract via file 3_, this essentially spams the contract with account args/references in groups of 4 per app call using the "Accumulate Weight for Snapshot Round" method, checking if all accounts meet eligibility via TEAL logic. If an account meets all conditions, the valid signature counter increments, as well as the algo commitment to consensus from the signer's account.
- The commitment snapshots submitted en masse must be preceded by a "Set Snapshot Round" method call, and all snapshot requests must occur within the same round (There may be issues with scalability in the future, so it may be reasonable to create a window of 2-3 rounds or more for all snapshot requests, however it is not impossible that someone can move an excess of funds to another account registered to increase the weight or create eligibility for additional accounts.)

## Step 6 (Reset Signature Flags):
- Once a commitment snapshot round is over, the flags on each signature can be reset to False, or "Uncounted", should a recount be necessary; there is no deadline for petition signatures, so snapshots can be done as many times as the petitioner would like.
  *Note: Once the "Set Snapshot Round" method is called before commitment snapshot calls, the global states are reset for valid signature counts and accumulated algorand weight. This information is not lost as global state deltas are always on-chain, but will only be viewable from the global state delta of the "Set Snapshot Round" transaction.*
  
