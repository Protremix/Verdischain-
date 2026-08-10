#!/usr/bin/env python3
"""Apply IBC hardening fixes to the Verdis Chain codebase on the remote server."""
import subprocess
import sys
import textwrap

def ssh_run(cmd, timeout=30):
    """Run a command on the server via SSH."""
    result = subprocess.run(
        ["ssh", "root@91.98.160.145", cmd],
        capture_output=True, text=True, timeout=timeout
    )
    return result.stdout + result.stderr

# Write the Python fix script to the server
fix_script = r'''
import re

with open("/opt/verdis-chain-rust/pallets/ibc/src/lib.rs", "r") as f:
    content = f.read()

# 1. Gate create_client behind root
old = """            let _who = ensure_signed(origin)?;

            let client_id = IbcClientCounter::<T>::get();"""
new = """            // SECURITY: Only root/governance can create IBC clients
            ensure_root(origin)?;

            let client_id = IbcClientCounter::<T>::get();"""
assert old in content, "Could not find create_client"
content = content.replace(old, new)

# 2. Gate open_connection behind root
old2 = """            let _who = ensure_signed(origin)?;

            let client = IbcClients::<T>::get(client_id).ok_or(Error::<T>::ClientNotFound)?;"""
new2 = """            // SECURITY: Only root/governance can open IBC connections
            ensure_root(origin)?;

            let client = IbcClients::<T>::get(client_id).ok_or(Error::<T>::ClientNotFound)?;"""
assert old2 in content, "Could not find open_connection"
content = content.replace(old2, new2)

# 3. Gate open_channel behind root
old3 = """            let _who = ensure_signed(origin)?;

            let connection =
                IbcConnections::<T>::get(connection_id).ok_or(Error::<T>::ConnectionNotFound)?;"""
new3 = """            // SECURITY: Only root/governance can open IBC channels
            ensure_root(origin)?;

            let connection =
                IbcConnections::<T>::get(connection_id).ok_or(Error::<T>::ConnectionNotFound)?;"""
assert old3 in content, "Could not find open_channel"
content = content.replace(old3, new3)

# 4. Add timeout_height validation in send_packet
old4 = """            let channel = IbcChannels::<T>::get(channel_id).ok_or(Error::<T>::ChannelNotFound)?;
            ensure!(channel.state == 3, Error::<T>::ChannelNotOpen);
            ensure!(
                data.len() as u32 <= T::MaxPacketDataLen::get(),
                Error::<T>::PacketDataTooLarge
            );

            let sequence = IbcNextSequenceSend::<T>::get(channel_id);"""
new4 = """            let channel = IbcChannels::<T>::get(channel_id).ok_or(Error::<T>::ChannelNotFound)?;
            ensure!(channel.state == 3, Error::<T>::ChannelNotOpen);
            ensure!(
                data.len() as u32 <= T::MaxPacketDataLen::get(),
                Error::<T>::PacketDataTooLarge
            );
            // SECURITY: timeout_height must be in the future
            let current_height: u64 = frame_system::Pallet::<T>::block_number()
                .try_into()
                .unwrap_or(0);
            ensure!(
                timeout_height > current_height,
                Error::<T>::PacketTimeout
            );

            let sequence = IbcNextSequenceSend::<T>::get(channel_id);"""
assert old4 in content, "Could not find send_packet body"
content = content.replace(old4, new4)

# 5. Add update_client and freeze_client functions after close_channel
old5 = """            Self::deposit_event(Event::ChannelClosed { channel_id });
            Ok(())
        }
    }

    impl<T: Config> Pallet<T> {"""
new5 = """            Self::deposit_event(Event::ChannelClosed { channel_id });
            Ok(())
        }

        /// Update a light client's latest height
        #[pallet::call_index(9)]
        #[pallet::weight(Weight::from_parts(10_000, 0))]
        pub fn update_client(
            origin: OriginFor<T>,
            client_id: u32,
            new_height: u64,
        ) -> DispatchResult {
            // SECURITY: Only root/governance can update client state
            ensure_root(origin)?;

            let mut client =
                IbcClients::<T>::get(client_id).ok_or(Error::<T>::ClientNotFound)?;
            ensure!(!client.frozen, Error::<T>::ClientFrozen);
            // SECURITY: Height must advance (no regressions)
            ensure!(
                new_height > client.latest_height,
                Error::<T>::InvalidSequence
            );
            client.latest_height = new_height;
            IbcClients::<T>::insert(client_id, client);
            Ok(())
        }

        /// Freeze a light client (on misbehavior or suspected fault)
        #[pallet::call_index(10)]
        #[pallet::weight(Weight::from_parts(5_000, 0))]
        pub fn freeze_client(
            origin: OriginFor<T>,
            client_id: u32,
        ) -> DispatchResult {
            // SECURITY: Only root/governance can freeze clients
            ensure_root(origin)?;

            let mut client =
                IbcClients::<T>::get(client_id).ok_or(Error::<T>::ClientNotFound)?;
            client.frozen = true;
            IbcClients::<T>::insert(client_id, client);
            Ok(())
        }
    }

    impl<T: Config> Pallet<T> {"""
assert old5 in content, "Could not find close_channel end"
content = content.replace(old5, new5)

# 6. Check client frozen state in transfer
old6 = """            let channel = IbcChannels::<T>::get(channel_id).ok_or(Error::<T>::ChannelNotFound)?;
            ensure!(channel.state == 3, Error::<T>::ChannelNotOpen);

            // CRITICAL FIX: Escrow tokens from sender to pallet account"""
new6 = """            let channel = IbcChannels::<T>::get(channel_id).ok_or(Error::<T>::ChannelNotFound)?;
            ensure!(channel.state == 3, Error::<T>::ChannelNotOpen);

            // SECURITY: Verify the connection's client is not frozen
            let connection = IbcConnections::<T>::get(channel.connection_id)
                .ok_or(Error::<T>::ConnectionNotFound)?;
            let client = IbcClients::<T>::get(connection.client_id)
                .ok_or(Error::<T>::ClientNotFound)?;
            ensure!(!client.frozen, Error::<T>::ClientFrozen);

            // CRITICAL FIX: Escrow tokens from sender to pallet account"""
assert old6 in content, "Could not find transfer body"
content = content.replace(old6, new6)

with open("/opt/verdis-chain-rust/pallets/ibc/src/lib.rs", "w") as f:
    f.write(content)
print("IBC hardened OK - 6 fixes applied")
'''

# Copy script to server and run it
proc = subprocess.Popen(
    ["ssh", "root@91.98.160.145", "python3 -c 'import sys; exec(sys.stdin.read())'"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)
stdout, stderr = proc.communicate(input=fix_script, timeout=30)
print(stdout)
if stderr:
    print("STDERR:", stderr)
