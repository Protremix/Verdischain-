#![cfg_attr(not(feature = "std"), no_std, no_main)]

// DELIBERATELY VULNERABLE contract, used to prove the checker actually finds bugs.
// A checker that only ever says "clean" is worse than no checker, so this file contains
// one instance of each vulnerability class the tool claims to detect.

#[ink::contract]
mod vulnerable_vault {
    use ink::storage::Mapping;

    #[ink(storage)]
    pub struct VulnerableVault {
        owner: AccountId,
        total_supply: Balance,
        balances: Mapping<AccountId, Balance>,
        // STORAGE-1: unbounded growth, any caller can append
        depositors: Vec<AccountId>,
    }

    impl VulnerableVault {
        #[ink(constructor)]
        pub fn new() -> Self {
            Self {
                owner: Self::env().caller(),
                total_supply: 0,
                balances: Mapping::default(),
                depositors: Vec::new(),
            }
        }

        // ARITH-1: raw += on a balance. In release builds this WRAPS instead of panicking.
        #[ink(message, payable)]
        pub fn deposit(&mut self) {
            let caller = self.env().caller();
            let amount = self.env().transferred_value();
            let mut balance = self.balances.get(caller).unwrap_or_default();
            balance += amount;
            self.total_supply += amount;
            self.balances.insert(caller, &balance);
            self.depositors.push(caller);
        }

        // ACCESS-1: no owner check at all - anyone can call this and drain the vault.
        #[ink(message)]
        pub fn withdraw_all(&mut self, to: AccountId) {
            let amount = self.env().balance();
            // REENTRANCY-1: external transfer happens BEFORE state is cleared
            self.env().transfer(to, amount).unwrap();
            self.total_supply = 0;
        }

        // ARITH-2 + PANIC-1: unwrap on user-controlled input, and an explicit panic
        #[ink(message)]
        pub fn force_take(&mut self, from: AccountId, amount: Balance) {
            let balance = self.balances.get(from).unwrap();
            if balance < amount {
                panic!("not enough");
            }
            self.balances.insert(from, &(balance - amount));
        }

        // ACCESS-1: privileged setter with no caller check
        #[ink(message)]
        pub fn set_owner(&mut self, new_owner: AccountId) {
            self.owner = new_owner;
        }

        // RANDOM-1: block data used to pick a winner - block producers can influence this
        #[ink(message)]
        pub fn pick_winner(&self) -> AccountId {
            let seed = self.env().block_timestamp();
            let idx = (seed as usize) % self.depositors.len();
            self.depositors[idx]
        }

        // ACCESS-1: mint with no authorisation
        #[ink(message)]
        pub fn mint(&mut self, to: AccountId, value: Balance) {
            let b = self.balances.get(to).unwrap_or_default();
            self.balances.insert(to, &(b + value));
            self.total_supply += value;
        }
    }
}
