#!/usr/bin/env python3
"""Patch IBC pallet with security hardening fixes."""
import sys

with open("lib.rs", "r") as f:
    content = f.read()

# 1. Add new errors
old_errors = "        PacketTimeout,"
new_errors = """        PacketTimeout,
        HeightJumpTooLarge,
        PacketNotAcknowledged,"""
content = content.replace(old_errors, new_errors, 1)

# 2. Add MaxHeightJump config constant
old_config = "        type MaxTransferAmount: Get<u128>;"
new_config = """        type MaxTransferAmount: Get<u128>;
        /// Maximum height jump per update_client call
        type MaxHeightJump: Get<u64>;"""
content = content.replace(old_config, new_config, 1)

# 3. Fix acknowledge_packet - verify packet exists before removing
old_ack = """        pub fn acknowledge_packet(
            origin: OriginFor<T>,
            channel_id: u32,
            sequence: u64,
        ) -> DispatchResult {
            let _who = ensure_signed(origin)?;

            IbcPackets::<T>::remove((channel_id, sequence));"""
new_ack = """        pub fn acknowledge_packet(
            origin: OriginFor<T>,
            channel_id: u32,
            sequence: u64,
        ) -> DispatchResult {
            let _who = ensure_signed(origin)?;

            // SECURITY: Verify packet exists before removing (prevent silent no-ops)
            ensure!(
                IbcPackets::<T>::contains_key((channel_id, sequence)),
                Error::<T>::PacketNotAcknowledged
            );
            IbcPackets::<T>::remove((channel_id, sequence));"""
content = content.replace(old_ack, new_ack, 1)

# 4. Fix recv_packet - check counterparty client not frozen + height validation
old_recv = """            let channel = IbcChannels::<T>::get(channel_id).ok_or(Error::<T>::ChannelNotFound)?;
            ensure!(channel.state == 3, Error::<T>::ChannelNotOpen);

            let expected_seq = IbcNextSequenceRecv::<T>::get(channel_id);"""
new_recv = """            let channel = IbcChannels::<T>::get(channel_id).ok_or(Error::<T>::ChannelNotFound)?;
            ensure!(channel.state == 3, Error::<T>::ChannelNotOpen);

            // SECURITY: Verify the connection's client is not frozen
            let connection = IbcConnections::<T>::get(channel.connection_id)
                .ok_or(Error::<T>::ConnectionNotFound)?;
            let client = IbcClients::<T>::get(connection.client_id)
                .ok_or(Error::<T>::ClientNotFound)?;
            ensure!(!client.frozen, Error::<T>::ClientFrozen);

            let expected_seq = IbcNextSequenceRecv::<T>::get(channel_id);"""
content = content.replace(old_recv, new_recv, 1)

# 5. Fix update_client - add height jump bound
old_update = """            ensure!(
                new_height > client.latest_height,
                Error::<T>::InvalidSequence
            );
            client.latest_height = new_height;"""
new_update = """            ensure!(
                new_height > client.latest_height,
                Error::<T>::InvalidSequence
            );
            // SECURITY: Bound height jump to prevent arbitrary jumps
            let jump = new_height.saturating_sub(client.latest_height);
            ensure!(
                jump <= T::MaxHeightJump::get(),
                Error::<T>::HeightJumpTooLarge
            );
            client.latest_height = new_height;"""
content = content.replace(old_update, new_update, 1)

with open("lib.rs", "w") as f:
    f.write(content)
print("IBC pallet patched successfully")
