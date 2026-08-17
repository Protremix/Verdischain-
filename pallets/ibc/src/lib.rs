#![allow(clippy::incompatible_msrv)]
#![allow(
    clippy::let_unit_value,
    deprecated,
    clippy::clone_on_copy,
    clippy::type_complexity,
    clippy::needless_borrow,
    clippy::collapsible_if,
    clippy::redundant_closure,
    clippy::manual_saturating_arithmetic,
    clippy::unnecessary_cast,
    clippy::derivable_impls,
    clippy::manual_checked_ops,
    clippy::needless_borrows_for_generic_args
)]
//! Inter-Blockchain Communication (IBC) Pallet for Verdis Chain

#![cfg_attr(not(feature = "std"), no_std)]
pub mod weights;
use codec::{Decode, Encode};
use frame_support::dispatch::DispatchResult;
use frame_support::traits::Currency;
use scale_info::TypeInfo;
use sp_runtime::traits::AccountIdConversion;
use sp_std::vec::Vec;
pub use weights::SubstrateWeight;
use weights::WeightInfo;

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use super::*;
    use frame_support::pallet_prelude::*;
    use frame_system::pallet_prelude::*;

    // ============ Types ============

    #[derive(Encode, Decode, Clone, PartialEq, Eq, TypeInfo, Default)]
    pub struct ClientState {
        pub chain_id: u32,
        pub latest_height: u64,
        pub trusting_period: u64,
        pub frozen: bool,
    }

    #[derive(Encode, Decode, Clone, PartialEq, Eq, TypeInfo, Default)]
    pub struct ConnectionEnd {
        pub client_id: u32,
        pub counterparty_client_id: u32,
        pub state: u8, // 0=Uninit, 1=Init, 2=TryOpen, 3=Open
    }

    #[derive(Encode, Decode, Clone, PartialEq, Eq, TypeInfo, Default)]
    pub struct ChannelEnd {
        pub ordering: u8, // 0=Ordered, 1=Unordered
        pub connection_id: u32,
        pub state: u8, // 0=Uninit, 1=Init, 2=TryOpen, 3=Open, 4=Closed
        pub counterparty_channel_id: Option<u32>,
        pub port_id: Vec<u8>,
    }

    #[derive(Encode, Decode, Clone, PartialEq, Eq, TypeInfo, Default)]
    pub struct Packet {
        pub sequence: u64,
        pub source_port: Vec<u8>,
        pub source_channel: u32,
        pub destination_port: Vec<u8>,
        pub destination_channel: u32,
        pub data: Vec<u8>,
        pub timeout_height: u64,
        /// Absolute timestamp (ms) after which packet times out. 0 = no timestamp timeout.
        pub timeout_timestamp: u64,
    }

    #[derive(Encode, Decode, Clone, PartialEq, Eq, TypeInfo, Default)]
    pub struct FungibleTokenPacketData {
        pub denom: Vec<u8>,
        pub amount: u128,
        pub sender: Vec<u8>,
        pub receiver: Vec<u8>,
    }

    // ============ Storage ============

    #[pallet::storage]
    #[pallet::getter(fn ibc_client_counter)]
    pub type IbcClientCounter<T> = StorageValue<_, u32, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn ibc_connection_counter)]
    pub type IbcConnectionCounter<T> = StorageValue<_, u32, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn ibc_channel_counter)]
    pub type IbcChannelCounter<T> = StorageValue<_, u32, ValueQuery>;

    #[pallet::storage]
    pub type IbcClients<T> = StorageMap<_, Blake2_128Concat, u32, ClientState>;

    #[pallet::storage]
    pub type IbcConnections<T> = StorageMap<_, Blake2_128Concat, u32, ConnectionEnd>;

    #[pallet::storage]
    pub type IbcChannels<T> = StorageMap<_, Blake2_128Concat, u32, ChannelEnd>;

    #[pallet::storage]
    pub type IbcPackets<T> = StorageMap<_, Blake2_128Concat, (u32, u64), Packet>;

    #[pallet::storage]
    pub type IbcNextSequenceSend<T> = StorageMap<_, Blake2_128Concat, u32, u64, ValueQuery>;

    #[pallet::storage]
    pub type IbcNextSequenceRecv<T> = StorageMap<_, Blake2_128Concat, u32, u64, ValueQuery>;

    #[pallet::storage]
    pub type IbcNextSequenceAck<T> = StorageMap<_, Blake2_128Concat, u32, u64, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn ibc_total_transfers)]
    pub type IbcTotalTransfers<T> = StorageValue<_, u64, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn ibc_total_volume)]
    pub type IbcTotalVolume<T> = StorageValue<_, u128, ValueQuery>;

    /// Failed refund entries that can be retried via governance
    #[pallet::storage]
    pub type FailedRefunds<T: Config> =
        StorageMap<_, Blake2_128Concat, (u32, u64), (T::AccountId, BalanceOf<T>), OptionQuery>;

    /// Designated relayer per channel for packet acknowledgement authorization
    #[pallet::storage]
    pub type ChannelRelayers<T: Config> = StorageMap<_, Blake2_128Concat, u32, T::AccountId, OptionQuery>;

    /// Packet receipts to prevent replay on recv_packet
    #[pallet::storage]
    pub type IbcPacketReceipts<T> = StorageMap<_, Blake2_128Concat, (u32, u64), (), OptionQuery>;

    // ============ Config ============

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type WeightInfo: WeightInfo;
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        type MaxPortIdLen: Get<u32>;
        type MaxPacketDataLen: Get<u32>;
        /// Currency for escrowing cross-chain transfers
        type Currency: frame_support::traits::Currency<Self::AccountId>;
        /// Maximum transfer amount
        type MaxTransferAmount: Get<u128>;
        /// Maximum height jump per update_client call
        type MaxHeightJump: Get<u64>;
        /// Timestamp provider for timestamp-based timeouts (milliseconds)
        type TimestampProvider: Get<u64>;
    }

    // ============ Events ============

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        ClientCreated {
            client_id: u32,
            chain_id: u32,
        },
        ConnectionOpened {
            connection_id: u32,
            client_id: u32,
        },
        ChannelOpened {
            channel_id: u32,
            connection_id: u32,
            ordering: u8,
        },
        ChannelClosed {
            channel_id: u32,
        },
        PacketSent {
            channel_id: u32,
            sequence: u64,
            source_port: Vec<u8>,
        },
        PacketReceived {
            channel_id: u32,
            sequence: u64,
            dest_port: Vec<u8>,
        },
        PacketAcknowledged {
            channel_id: u32,
            sequence: u64,
        },
        PacketTimedOut {
            channel_id: u32,
            sequence: u64,
        },
        RefundFailed {
            channel_id: u32,
            sequence: u64,
            sender: T::AccountId,
            amount: BalanceOf<T>,
        },
        TransferInitiated {
            sender: T::AccountId,
            receiver: Vec<u8>,
            amount: u128,
            denom: Vec<u8>,
            channel_id: u32,
        },
        TokensReceived {
            channel_id: u32,
            sequence: u64,
            receiver: Vec<u8>,
            amount: u128,
            denom: Vec<u8>,
        },
        EscrowBurned {
            channel_id: u32,
            sequence: u64,
            amount: BalanceOf<T>,
        },
        EscrowRefunded {
            channel_id: u32,
            sequence: u64,
            sender: T::AccountId,
            amount: BalanceOf<T>,
        },
        ChannelRelayerSet {
            channel_id: u32,
            relayer: T::AccountId,
        },
    }

    // ============ Errors ============

    #[pallet::error]
    pub enum Error<T> {
        /// Packet has already been acknowledged
        PacketAlreadyAcknowledged,
        ClientNotFound,
        ConnectionNotFound,
        ChannelNotFound,
        PacketNotFound,
        ChannelNotOpen,
        InsufficientBalance,
        TransferAmountTooLarge,
        EscrowFailed,
        ConnectionNotOpen,
        ClientFrozen,
        InvalidSequence,
        PacketTimeout,
        HeightJumpTooLarge,
        PacketNotAcknowledged,
        PortIdTooLong,
        PacketDataTooLarge,
        UnauthorizedRelayer,
        PacketAlreadyReceived,
        InvalidPacketData,
        ChannelRelayerNotSet,
    }

    type BalanceOf<T> =
        <<T as Config>::Currency as Currency<<T as frame_system::Config>::AccountId>>::Balance;

    // ============ Pallet ============

    #[pallet::pallet]
    #[pallet::without_storage_info]
    pub struct Pallet<T>(_);

    // ============ Dispatchable Functions ============

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Create a new light client
        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::create_client())]
        pub fn create_client(
            origin: OriginFor<T>,
            chain_id: u32,
            initial_height: u64,
            trusting_period: u64,
        ) -> DispatchResult {
            // SECURITY: Only root/governance can create IBC clients
            ensure_root(origin)?;

            let client_id = IbcClientCounter::<T>::get();
            IbcClientCounter::<T>::put(client_id.checked_add(1).unwrap_or(u32::MAX));

            let client_state = ClientState {
                chain_id,
                latest_height: initial_height,
                trusting_period,
                frozen: false,
            };

            IbcClients::<T>::insert(client_id, client_state);
            Self::deposit_event(Event::ClientCreated {
                client_id,
                chain_id,
            });
            Ok(())
        }

        /// Open a connection
        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::open_connection())]
        pub fn open_connection(
            origin: OriginFor<T>,
            client_id: u32,
            counterparty_client_id: u32,
        ) -> DispatchResult {
            // SECURITY: Only root/governance can open IBC connections
            ensure_root(origin)?;

            let client = IbcClients::<T>::get(client_id).ok_or(Error::<T>::ClientNotFound)?;
            ensure!(!client.frozen, Error::<T>::ClientFrozen);

            let connection_id = IbcConnectionCounter::<T>::get();
            IbcConnectionCounter::<T>::put(connection_id.checked_add(1).unwrap_or(u32::MAX));

            let connection = ConnectionEnd {
                client_id,
                counterparty_client_id,
                state: 3, // Open
            };

            IbcConnections::<T>::insert(connection_id, connection);
            Self::deposit_event(Event::ConnectionOpened {
                connection_id,
                client_id,
            });
            Ok(())
        }

        /// Open a channel
        #[pallet::call_index(2)]
        #[pallet::weight(T::WeightInfo::open_channel())]
        pub fn open_channel(
            origin: OriginFor<T>,
            connection_id: u32,
            ordering: u8,
            port_id: Vec<u8>,
        ) -> DispatchResult {
            // SECURITY: Only root/governance can open IBC channels
            ensure_root(origin)?;

            let connection =
                IbcConnections::<T>::get(connection_id).ok_or(Error::<T>::ConnectionNotFound)?;
            ensure!(connection.state == 3, Error::<T>::ConnectionNotOpen);
            ensure!(
                port_id.len() as u32 <= T::MaxPortIdLen::get(),
                Error::<T>::PortIdTooLong
            );

            let channel_id = IbcChannelCounter::<T>::get();
            IbcChannelCounter::<T>::put(channel_id.checked_add(1).unwrap_or(u32::MAX));

            let channel = ChannelEnd {
                ordering,
                connection_id,
                state: 3, // Open
                counterparty_channel_id: None,
                port_id: port_id.clone(),
            };

            IbcChannels::<T>::insert(channel_id, channel);
            IbcNextSequenceSend::<T>::insert(channel_id, 1u64);
            IbcNextSequenceRecv::<T>::insert(channel_id, 1u64);
            IbcNextSequenceAck::<T>::insert(channel_id, 1u64);

            Self::deposit_event(Event::ChannelOpened {
                channel_id,
                connection_id,
                ordering,
            });
            Ok(())
        }

        /// Send a packet
        #[pallet::call_index(3)]
        #[pallet::weight(T::WeightInfo::send_packet())]
        pub fn send_packet(
            origin: OriginFor<T>,
            channel_id: u32,
            source_port: Vec<u8>,
            dest_port: Vec<u8>,
            data: Vec<u8>,
            timeout_height: u64,
            timeout_timestamp: u64,
        ) -> DispatchResult {
            let _who = ensure_signed(origin)?;

            let channel = IbcChannels::<T>::get(channel_id).ok_or(Error::<T>::ChannelNotFound)?;
            ensure!(channel.state == 3, Error::<T>::ChannelNotOpen);
            ensure!(
                data.len() as u32 <= T::MaxPacketDataLen::get(),
                Error::<T>::PacketDataTooLarge
            );
            // SECURITY: timeout_height must be in the future
            let current_height: u64 = frame_system::Pallet::<T>::block_number()
                .try_into()
                .unwrap_or(0);
            ensure!(timeout_height > current_height, Error::<T>::PacketTimeout);

            let sequence = IbcNextSequenceSend::<T>::get(channel_id);
            IbcNextSequenceSend::<T>::insert(
                channel_id,
                sequence.checked_add(1).unwrap_or(u64::MAX),
            );

            let packet = Packet {
                sequence,
                source_port: source_port.clone(),
                source_channel: channel_id,
                destination_port: dest_port,
                destination_channel: channel_id,
                data,
                timeout_height,
                timeout_timestamp,
            };

            IbcPackets::<T>::insert((channel_id, sequence), packet);
            Self::deposit_event(Event::PacketSent {
                channel_id,
                sequence,
                source_port,
            });
            Ok(())
        }

        /// Receive a packet
        #[pallet::call_index(4)]
        #[pallet::weight(T::WeightInfo::recv_packet())]
        pub fn recv_packet(
            origin: OriginFor<T>,
            channel_id: u32,
            sequence: u64,
            dest_port: Vec<u8>,
            data: Vec<u8>,
        ) -> DispatchResult {
            let _who = ensure_signed(origin)?;

            let channel = IbcChannels::<T>::get(channel_id).ok_or(Error::<T>::ChannelNotFound)?;
            ensure!(channel.state == 3, Error::<T>::ChannelNotOpen);

            // SECURITY: Verify the connection's client is not frozen
            let connection = IbcConnections::<T>::get(channel.connection_id)
                .ok_or(Error::<T>::ConnectionNotFound)?;
            let client =
                IbcClients::<T>::get(connection.client_id).ok_or(Error::<T>::ClientNotFound)?;
            ensure!(!client.frozen, Error::<T>::ClientFrozen);

            // FIX C7: Verify the packet sequence matches expected (no gaps/replay)
            let expected_seq = IbcNextSequenceRecv::<T>::get(channel_id);
            ensure!(sequence == expected_seq, Error::<T>::InvalidSequence);

            // FIX C7: Check for replay — if a receipt already exists, reject
            ensure!(
                !IbcPacketReceipts::<T>::contains_key((channel_id, sequence)),
                Error::<T>::PacketAlreadyReceived
            );

            IbcNextSequenceRecv::<T>::insert(
                channel_id,
                sequence.checked_add(1).unwrap_or(u64::MAX),
            );

            // FIX C7: Store the packet commitment/receipt to prevent replay
            IbcPacketReceipts::<T>::insert((channel_id, sequence), ());

            // FIX C7: Parse the packet data and mint/credit tokens to the receiver
            // Attempt to decode as FungibleTokenPacketData (SCALE-encoded)
            let ft_data = FungibleTokenPacketData::decode(&mut data.as_slice());

            if let Ok(ft_data) = ft_data {
                // Decode receiver address from Vec<u8> to T::AccountId
                if let Ok(receiver_account) =
                    T::AccountId::decode(&mut ft_data.receiver.as_slice())
                {
                    let mint_amount: BalanceOf<T> = ft_data
                        .amount
                        .try_into()
                        .map_err(|_| Error::<T>::TransferAmountTooLarge)?;

                    // Mint tokens to the receiver's account
                    let _imbalance =
                        T::Currency::deposit_creating(&receiver_account, mint_amount);

                    Self::deposit_event(Event::TokensReceived {
                        channel_id,
                        sequence,
                        receiver: ft_data.receiver.clone(),
                        amount: ft_data.amount,
                        denom: ft_data.denom.clone(),
                    });
                }
            }

            Self::deposit_event(Event::PacketReceived {
                channel_id,
                sequence,
                dest_port,
            });
            Ok(())
        }

        /// Acknowledge a packet
        #[pallet::call_index(5)]
        #[pallet::weight(T::WeightInfo::acknowledge_packet())]
        pub fn acknowledge_packet(
            origin: OriginFor<T>,
            channel_id: u32,
            sequence: u64,
            ack_success: bool,
        ) -> DispatchResult {
            // FIX C6: Authentication — only the designated relayer for the channel
            // can acknowledge packets. If no relayer is set, fall back to root.
            match ChannelRelayers::<T>::get(channel_id) {
                Some(designated_relayer) => {
                    let who = ensure_signed(origin)?;
                    ensure!(who == designated_relayer, Error::<T>::UnauthorizedRelayer);
                }
                None => {
                    ensure_root(origin)?;
                }
            }

            // SECURITY: Verify packet exists before removing (prevent silent no-ops)
            ensure!(
                IbcPackets::<T>::contains_key((channel_id, sequence)),
                Error::<T>::PacketNotAcknowledged
            );

            // FIX H8: Get packet data BEFORE removing to handle escrow lifecycle
            let packet_data = Self::get_packet_data(&channel_id, &sequence);
            IbcPackets::<T>::remove((channel_id, sequence));
            let next_ack = IbcNextSequenceAck::<T>::get(channel_id);
            IbcNextSequenceAck::<T>::insert(
                channel_id,
                next_ack.checked_add(1).unwrap_or(u64::MAX),
            );

            // FIX H8: Complete the IBC lifecycle for outgoing transfers.
            // On successful ack: burn the escrowed tokens (they have been minted on dest chain).
            // On failed ack: refund the escrowed tokens to the sender.
            if let Some(ft_data) = packet_data {
                let pallet_account = Self::account_id();
                let escrow_amount: BalanceOf<T> = ft_data
                    .amount
                    .try_into()
                    .unwrap_or_else(|_| BalanceOf::<T>::zero());

                if ack_success {
                    // Successful acknowledgement — burn escrowed tokens
                    let _ = T::Currency::slash(&pallet_account, escrow_amount);
                    Self::deposit_event(Event::EscrowBurned {
                        channel_id,
                        sequence,
                        amount: escrow_amount,
                    });
                } else {
                    // Failed acknowledgement — refund escrowed tokens to sender
                    if let Ok(sender) = T::AccountId::decode(&mut ft_data.sender.as_slice()) {
                        let refund_result = T::Currency::transfer(
                            &pallet_account,
                            &sender,
                            escrow_amount,
                            frame_support::traits::ExistenceRequirement::AllowDeath,
                        );
                        if refund_result.is_err() {
                            FailedRefunds::<T>::insert(
                                (channel_id, sequence),
                                (sender.clone(), escrow_amount),
                            );
                            Self::deposit_event(Event::RefundFailed {
                                channel_id,
                                sequence,
                                sender,
                                amount: escrow_amount,
                            });
                        } else {
                            Self::deposit_event(Event::EscrowRefunded {
                                channel_id,
                                sequence,
                                sender,
                                amount: escrow_amount,
                            });
                        }
                    }
                }
            }

            Self::deposit_event(Event::PacketAcknowledged {
                channel_id,
                sequence,
            });
            Ok(())
        }

        /// Timeout a packet
        #[pallet::call_index(6)]
        #[pallet::weight(T::WeightInfo::timeout_packet())]
        pub fn timeout_packet(
            origin: OriginFor<T>,
            channel_id: u32,
            sequence: u64,
        ) -> DispatchResult {
            // SECURITY: Any signed relayer can call timeout, but packet must not be acknowledged
            let _relayer = ensure_signed(origin)?;

            // SECURITY: Verify channel exists and is not closed
            let channel = IbcChannels::<T>::get(channel_id).ok_or(Error::<T>::ChannelNotFound)?;
            ensure!(channel.state != 4, Error::<T>::ChannelNotOpen);

            let packet =
                IbcPackets::<T>::get((channel_id, sequence)).ok_or(Error::<T>::PacketNotFound)?;

            // SECURITY: Verify the packet has actually timed out
            // A packet is timed out if EITHER:
            //   - current_height >= timeout_height (height-based timeout), OR
            //   - timeout_timestamp > 0 AND current_timestamp >= timeout_timestamp (timestamp-based timeout)
            let current_height: u64 = frame_system::Pallet::<T>::block_number()
                .try_into()
                .unwrap_or(0);
            let current_timestamp: u64 = T::TimestampProvider::get();

            let height_expired = current_height >= packet.timeout_height;
            let timestamp_expired =
                packet.timeout_timestamp > 0 && current_timestamp >= packet.timeout_timestamp;

            ensure!(
                height_expired || timestamp_expired,
                Error::<T>::PacketTimeout
            );

            // FIX: Get packet data BEFORE removing, then refund escrowed tokens
            let packet_data = Self::get_packet_data(&channel_id, &sequence);
            IbcPackets::<T>::remove((channel_id, sequence));

            if let Some(ft_data) = packet_data {
                let sender = T::AccountId::decode(&mut ft_data.sender.as_slice()).ok();
                if let Some(sender) = sender {
                    let pallet_account = Self::account_id();
                    let refund_amount: BalanceOf<T> = ft_data
                        .amount
                        .try_into()
                        .unwrap_or_else(|_| BalanceOf::<T>::zero());
                    let refund_result = T::Currency::transfer(
                        &pallet_account,
                        &sender,
                        refund_amount,
                        frame_support::traits::ExistenceRequirement::AllowDeath,
                    );
                    if refund_result.is_err() {
                        // SECURITY: Store failed refund for governance retry instead of losing tokens
                        FailedRefunds::<T>::insert(
                            (channel_id, sequence),
                            (sender.clone(), refund_amount),
                        );
                        Self::deposit_event(Event::RefundFailed {
                            channel_id,
                            sequence,
                            sender,
                            amount: refund_amount,
                        });
                    }
                }
            }

            Self::deposit_event(Event::PacketTimedOut {
                channel_id,
                sequence,
            });
            Ok(())
        }

        /// Cross-chain token transfer
        #[pallet::call_index(7)]
        #[pallet::weight(T::WeightInfo::transfer())]
        pub fn transfer(
            origin: OriginFor<T>,
            channel_id: u32,
            receiver: Vec<u8>,
            amount: u128,
            denom: Vec<u8>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            // CRITICAL FIX: Escrow tokens before creating transfer packet
            ensure!(amount > 0, Error::<T>::InsufficientBalance);
            ensure!(
                amount <= T::MaxTransferAmount::get(),
                Error::<T>::TransferAmountTooLarge
            );

            let channel = IbcChannels::<T>::get(channel_id).ok_or(Error::<T>::ChannelNotFound)?;
            ensure!(channel.state == 3, Error::<T>::ChannelNotOpen);

            // SECURITY: Verify the connection's client is not frozen
            let connection = IbcConnections::<T>::get(channel.connection_id)
                .ok_or(Error::<T>::ConnectionNotFound)?;
            let client =
                IbcClients::<T>::get(connection.client_id).ok_or(Error::<T>::ClientNotFound)?;
            ensure!(!client.frozen, Error::<T>::ClientFrozen);

            // CRITICAL FIX: Escrow tokens from sender to pallet account
            let pallet_account = Self::account_id();
            T::Currency::transfer(
                &who,
                &pallet_account,
                amount
                    .try_into()
                    .map_err(|_| Error::<T>::TransferAmountTooLarge)?,
                frame_support::traits::ExistenceRequirement::AllowDeath,
            )
            .map_err(|_| Error::<T>::EscrowFailed)?;

            let sequence = IbcNextSequenceSend::<T>::get(channel_id);
            IbcNextSequenceSend::<T>::insert(
                channel_id,
                sequence.checked_add(1).unwrap_or(u64::MAX),
            );

            let packet_data = FungibleTokenPacketData {
                denom: denom.clone(),
                amount,
                sender: who.encode(),
                receiver: receiver.clone(),
            };

            let timeout: u64 = frame_system::Pallet::<T>::block_number()
                .try_into()
                .unwrap_or(0)
                + 1000;

            let packet = Packet {
                sequence,
                source_port: b"transfer".to_vec(),
                source_channel: channel_id,
                destination_port: b"transfer".to_vec(),
                destination_channel: channel_id,
                data: packet_data.encode(),
                timeout_height: timeout,
                timeout_timestamp: 0,
            };

            IbcPackets::<T>::insert((channel_id, sequence), packet);
            IbcTotalTransfers::<T>::put(IbcTotalTransfers::<T>::get() + 1);
            IbcTotalVolume::<T>::put(IbcTotalVolume::<T>::get() + amount);

            Self::deposit_event(Event::TransferInitiated {
                sender: who,
                receiver,
                amount,
                denom,
                channel_id,
            });
            Ok(())
        }

        /// Close a channel
        #[pallet::call_index(8)]
        #[pallet::weight(T::WeightInfo::close_channel())]
        pub fn close_channel(origin: OriginFor<T>, channel_id: u32) -> DispatchResult {
            ensure_root(origin)?;

            IbcChannels::<T>::mutate(channel_id, |channel| {
                if let Some(c) = channel {
                    c.state = 4; // Closed
                }
            });

            Self::deposit_event(Event::ChannelClosed { channel_id });
            Ok(())
        }

        /// Update a light client's latest height
        #[pallet::call_index(9)]
        #[pallet::weight(T::WeightInfo::update_client())]
        pub fn update_client(
            origin: OriginFor<T>,
            client_id: u32,
            new_height: u64,
        ) -> DispatchResult {
            // SECURITY: Only root/governance can update client state
            ensure_root(origin)?;

            let mut client = IbcClients::<T>::get(client_id).ok_or(Error::<T>::ClientNotFound)?;
            ensure!(!client.frozen, Error::<T>::ClientFrozen);
            // SECURITY: Height must advance (no regressions)
            ensure!(
                new_height > client.latest_height,
                Error::<T>::InvalidSequence
            );
            // SECURITY: Bound height jump to prevent arbitrary jumps
            let jump = new_height.saturating_sub(client.latest_height);
            ensure!(
                jump <= T::MaxHeightJump::get(),
                Error::<T>::HeightJumpTooLarge
            );
            client.latest_height = new_height;
            IbcClients::<T>::insert(client_id, client);
            Ok(())
        }

        /// Freeze a light client (on misbehavior or suspected fault)
        #[pallet::call_index(10)]
        #[pallet::weight(Weight::from_parts(5_000, 0))]
        pub fn freeze_client(origin: OriginFor<T>, client_id: u32) -> DispatchResult {
            // SECURITY: Only root/governance can freeze clients
            ensure_root(origin)?;

            let mut client = IbcClients::<T>::get(client_id).ok_or(Error::<T>::ClientNotFound)?;
            client.frozen = true;
            IbcClients::<T>::insert(client_id, client);
            Ok(())
        }

        /// FIX C6: Set the designated relayer for a channel.
        /// Only root/governance can set the relayer.
        #[pallet::call_index(11)]
        #[pallet::weight(T::WeightInfo::set_channel_relayer())]
        pub fn set_channel_relayer(
            origin: OriginFor<T>,
            channel_id: u32,
            relayer: T::AccountId,
        ) -> DispatchResult {
            ensure_root(origin)?;
            ChannelRelayers::<T>::insert(channel_id, relayer.clone());
            Self::deposit_event(Event::ChannelRelayerSet {
                channel_id,
                relayer,
            });
            Ok(())
        }
    }

    impl<T: Config> Pallet<T> {
        /// Pallet account for escrowing cross-chain transfers
        pub fn account_id() -> T::AccountId {
            let pallet_id = frame_support::PalletId(*b"verdisib");
            pallet_id.into_account_truncating()
        }

        /// Decode packet data for refund logic
        fn get_packet_data(channel_id: &u32, sequence: &u64) -> Option<FungibleTokenPacketData> {
            IbcPackets::<T>::get((*channel_id, *sequence))
                .and_then(|p| FungibleTokenPacketData::decode(&mut p.data.as_slice()).ok())
        }

        pub fn get_stats() -> (u32, u32, u32, u64, u128) {
            (
                IbcClientCounter::<T>::get(),
                IbcConnectionCounter::<T>::get(),
                IbcChannelCounter::<T>::get(),
                IbcTotalTransfers::<T>::get(),
                IbcTotalVolume::<T>::get(),
            )
        }

        pub fn is_channel_open(channel_id: u32) -> bool {
            IbcChannels::<T>::get(channel_id)
                .map(|c| c.state == 3)
                .unwrap_or(false)
        }
    }
}

#[cfg(test)]
mod tests;

#[cfg(feature = "runtime-benchmarks")]
mod benchmarking;
