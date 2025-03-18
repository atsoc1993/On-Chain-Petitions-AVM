from algopy import ARC4Contract, UInt64, arc4, Application, subroutine, Global, BoxMap, gtxn, Txn, String, itxn, op, urange
from algopy.arc4 import abimethod, Struct, Address, DynamicArray, Bool
import typing as t

class Signer(Struct):
    address: Address

class SignatureCountedFlag(Struct):
    flag: Bool

class AccountSet(Struct):
    accounts: DynamicArray[Address]
    
class SnapshotPetition(ARC4Contract, avm_version=11):
    def __init__(self) -> None:
        self.total_petitioners = UInt64(0)
        self.last_snapshot_total_valid_petitioners = UInt64(0)
        self.last_snapshot_round = UInt64(0)
        self.last_snapshot_weight_in_algo = UInt64(0)
        self.signer_box = BoxMap(Signer, SignatureCountedFlag, key_prefix='')
        self.petition_details = BoxMap(String, String, key_prefix='P')

    @subroutine
    def is_creator(
        self
    ) -> None:
        assert Txn.sender == Global.creator_address
        
    @abimethod
    def set_petition_details(
        self,
        petition_details: String,
        mbr_payment: gtxn.PaymentTransaction
    ) -> None:
        
        self.is_creator()
        self.petition_details_not_set_yet()
        self.valid_petition_details_mbr_payment(petition_details, mbr_payment)
        self.petition_details[String('Petition Details')] = petition_details 

    @subroutine
    def petition_details_not_set_yet(
        self,
    ) -> None:
        
        assert String('Petition Details') not in self.petition_details

    @subroutine
    def contract_is_receiver(
        self,
        mbr_payment: gtxn.PaymentTransaction
    ) -> None:
        
        assert mbr_payment.receiver == Global.current_application_address

    @subroutine
    def valid_petition_details_mbr_payment(
        self,
        petition_details: String,
        mbr_payment: gtxn.PaymentTransaction
    ) -> None:
        
        self.contract_is_receiver(mbr_payment)

        prefix_len = UInt64(1)
        box_name_byte_len = String('Petition Details').bytes.length
        box_value_byte_len = petition_details.bytes.length
        total_bytes_cost = (prefix_len + box_name_byte_len + box_value_byte_len) * 400
        create_box_cost = UInt64(2500)
        total_cost = total_bytes_cost + create_box_cost

        assert mbr_payment.amount >= total_cost

        self.refund_excess_mbr(mbr_payment, total_cost)


    @abimethod
    def sign_petition(
        self,
        mbr_payment: gtxn.PaymentTransaction
    ) -> None:

        self.valid_sign_mbr_payment(mbr_payment)
        signer = Signer(Address(Txn.sender))
        
        assert signer not in self.signer_box, "User has already signed this petition"

        self.signer_box[signer] = SignatureCountedFlag(Bool(False))
        self.total_petitioners += 1


    @subroutine
    def valid_sign_mbr_payment(
        self,
        mbr_payment: gtxn.PaymentTransaction
    ) -> None:
        
        self.contract_is_receiver(mbr_payment)

        box_name_byte_len = Txn.sender.bytes.length
        box_value_byte_len = UInt64(1)
        total_bytes_cost = (box_name_byte_len + box_value_byte_len) * 400
        create_box_cost = UInt64(2500)
        total_cost = total_bytes_cost + create_box_cost

        assert mbr_payment.amount >= total_cost

        self.refund_excess_mbr(mbr_payment, total_cost)

    @subroutine
    def refund_excess_mbr(
        self,
        mbr_payment: gtxn.PaymentTransaction,
        total_cost: UInt64
    ) -> None:
        
        if mbr_payment.amount > total_cost:
            itxn.Payment(
                receiver=Txn.sender,
                amount=mbr_payment.amount - total_cost
            ).submit()


    @abimethod
    def set_snapshot_round(
        self
    ) -> None:
        
        self.is_creator()
        assert self.last_snapshot_round != Global.round

        self.last_snapshot_total_valid_petitioners = UInt64(0)
        self.last_snapshot_weight_in_algo = UInt64(0)
        self.last_snapshot_round = Global.round

    @abimethod
    def reset_flags_for_recount(
        self,
        accounts: AccountSet
    ) -> None:

        self.is_creator()        
        assert Global.round != self.last_snapshot_round

        for i in urange(accounts.accounts.length):
            signer = Signer(accounts.accounts[i])
            self.signer_box[signer] = SignatureCountedFlag(Bool(False))
    

    @abimethod
    def accumulate_weight_for_snapshot_round(
        self,
        accounts: AccountSet
    ) -> None:
        
        self.is_creator()
        assert Global.round == self.last_snapshot_round

        for i in urange(accounts.accounts.length):
            
            address = accounts.accounts[i]
            signer = Signer(address)
            assert self.signer_box[signer] == SignatureCountedFlag(Bool(False))

            self.signer_box[signer] = SignatureCountedFlag(Bool(True))        

            account = address.native
            current_balance = account.balance

            incentive_eligible = False
            sufficient_balance = False
            sufficient_last_heartbeat = False

            #Check if the account is incentive eligible for this snapshot
            if op.AcctParamsGet.acct_incentive_eligible(account)[0]:
                incentive_eligible = True

            #Check if the account holds more than 10 Algo for this snapshot
            if account.balance > 10_000_000:
                sufficient_balance = True

            #Check if the account has had a heartbeat within the last 48 hours:
            '''
            "Heartbeats in Algorand are a mechanism to ensure nodes are operating properly. According to the documentation, accounts can be challenged randomly, 
            and when challenged, they must send a heartbeat within a specific timeframe.

            Specifically, challenges occur every ChallengeInterval rounds, which is currently set to 1000 rounds. During each challenge interval, 
            a randomly selected portion (currently 1/32) of all online accounts are challenged. These challenged accounts must send a heartbeat within 
            the ChallengeGracePeriod, which is currently 200 rounds, or they will be subject to suspension.

            With the current consensus parameters, nodes can expect to be challenged approximately daily. This helps ensure that nodes maintain good uptime, 
            as those with poor uptime would be suspended and would need to pay a fee to go back online." 
            '''

            #86,400 seconds per day, 2.8s~ blocks on average, 31,000~ blocks per day, a heartbeat must within the last 62,000 rounds

            last_heartbeat_round, has_a_last_heartbeat_round = op.AcctParamsGet.acct_last_heartbeat(account)
            if has_a_last_heartbeat_round:
                if Global.round - last_heartbeat_round > 62_000:
                    sufficient_last_heartbeat = True

            # You may customize this as you wish
            if incentive_eligible and sufficient_balance and sufficient_last_heartbeat:
                self.last_snapshot_weight_in_algo += current_balance
                self.last_snapshot_total_valid_petitioners += 1