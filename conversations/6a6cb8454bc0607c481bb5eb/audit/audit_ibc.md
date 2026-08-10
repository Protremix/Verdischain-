# IBC Pallet Security Review

## Summary Table

| # | Severity | Location | Issue |
|---|----------|----------|-------|
| 1 | CRITICAL | `acknowledge_packet` | No authorization or sequence validation — anyone can delete any packet |
| 2 | CRITICAL | `timeout_packet` | Inverted timeout logic — packets removed when NOT timed out |
| 3 | CRITICAL | `close_channel` | No authorization — anyone can close any channel |
| 4 | CRITICAL | `create_client` / `open_connection` / `open_channel` | Counter overflow causes ID collision and storage clobber |
| 5 | HIGH | `transfer` | `IbcTotalTransfers` and `IbcTotalVolume` overflow without checked arithmetic |
| 6 | HIGH | `transfer` | Timeout calculation overflows on `u64::MAX` block numbers |
| 7 | HIGH | `send_packet` | `sequence + 1` unchecked overflow; destination_channel hardcoded to source |
| 8 | HIGH | `recv_packet` | `sequence + 1` unchecked overflow; no packet commitment verification |
| 9 | HIGH | `acknowledge_packet` | `next_ack + 1` unchecked; ack sequence not validated against packet sequence |
| 10 | MEDIUM | `close_channel` | Channel state not validated before closing; no cleanup of pending packets |
| 11 | MEDIUM | `open_connection` | Connection opened directly to `Open` state — skips IBC handshake |
| 12 | MEDIUM | `open_channel` | Channel opened directly to `Open` state — skips IBC handshake |
| 13 | LOW | `timeout_packet` | Wrong error `ChannelNotFound` returned for missing packet |

---

## Finding 1 — CRITICAL: `acknowledge_packet` Has No Authorization or Sequence Validation

**Location:** `acknowledge_packet`

**Description:** Any signed account can call `acknowledge_packet` with any `(channel_id, sequence)` pair. The function removes the packet from storage and increments the ack sequence counter **without verifying**:
- That the packet exists
- That the caller is authorized
- That `sequence` matches the expected ack sequence

This allows an attacker to grief the protocol by deleting arbitrary in-flight packets and corrupting the ack sequence counter.

```rust
// BEFORE
pub fn acknowledge_packet(
    origin: OriginFor<T>,
    channel_id: u32,
    sequence: u64,
) -> DispatchResult {
    let _who = ensure_signed(origin)?;

    IbcPackets::<T>::remove((channel_id, sequence));
    let next_ack = IbcNextSequenceAck::<T>::get(channel_id);
    IbcNextSequenceAck::<T>::insert(channel_id, next_ack + 1);

    Self::deposit_event(Event::PacketAcknowledged {
        channel_id,
        sequence,
    });
    Ok(())
}

// AFTER
pub fn acknowledge_packet(
    origin: OriginFor<T>,
    channel_id: u32,
    sequence: u64,
) -> DispatchResult {
    ensure_root(origin)?; // Or a dedicated relayer whitelist origin

    // Verify packet exists before removing
    ensure!(
        IbcPackets::<T>::contains_key((channel_id, sequence)),
        Error::<T>::PacketNotFound
    );

    // Verify this is the next expected ack sequence
    let next_ack = IbcNextSequenceAck::<T>::get(channel_id);
    ensure!(sequence == next_ack, Error::<T>::InvalidSequence);

    IbcPackets::<T>::remove((channel_id, sequence));

    let new_next_ack = next_ack.checked_add(1).ok_or(Error::<T>::ArithmeticOverflow)?;
    IbcNextSequenceAck::<T>::insert(channel_id, new_next_ack);

    Self::deposit_event(Event::PacketAcknowledged {
        channel_id,
        sequence,
    });
    Ok(())
}
```

---

## Finding 2 — CRITICAL: `timeout_packet` Logic Is Inverted

**Location:** `timeout_packet`

**Description:** The `ensure!` condition removes a packet when `current_height >= timeout_height`, which is exactly **when the timeout is valid**. The error `PacketTimeout` fires when the packet has NOT yet timed out. The logic is inverted: it should error when the packet is still live, not when it has expired. As written, this prevents legitimate timeout processing and allows timeout of non-expired packets.

```rust
// BEFORE
ensure!(
    current_height >= packet.timeout_height,
    Error::<T>::PacketTimeout
);

// AFTER
// Error if the packet has NOT yet timed out (i.e., it is still valid)
ensure!(
    current_height >= packet.timeout_height,
    Error::<T>::PacketNotYetTimedOut // new error variant
);
```

Add the new error variant:
```rust
// In Error<T> enum — BEFORE (missing variant)
PacketTimeout,

// AFTER (rename existing + add correct semantic variant)
PacketNotYetTimedOut,  // Returned when timeout_packet called too early
PacketAlreadyTimedOut, // Optional: guard send_packet against zero timeout
```

---

## Finding 3 — CRITICAL: `close_channel` Has No Authorization

**Location:** `close_channel`

**Description:** Any signed account can close any channel at any time, immediately halting cross-chain communication for that channel. There is no check that the caller owns the channel, is a governance origin, or that the channel is in a closeable state (`Open`).

```rust
// BEFORE
pub fn close_channel(origin: OriginFor<T>, channel_id: u32) -> DispatchResult {
    let _who = ensure_signed(origin)?;

    IbcChannels::<T>::mutate(channel_id, |channel| {
        if let Some(c) = channel {
            c.state = 4; // Closed
        }
    });

    Self::deposit_event(Event::ChannelClosed { channel_id });
    Ok(())
}

// AFTER
pub fn close_channel(origin: OriginFor<T>, channel_id: u32) -> DispatchResult {
    ensure_root(origin)?; // Governance-gated; or use a channel owner map

    let channel = IbcChannels::<T>::get(channel_id)
        .ok_or(Error::<T>::ChannelNotFound)?;

    // Can only close a channel that is currently Open
    ensure!(channel.state == 3, Error::<T>::ChannelNotOpen);

    IbcChannels::<T>::mutate(channel_id, |ch| {
        if let Some(c) = ch {
            c.state = 4;
        }
    });

    Self::deposit_event(Event::ChannelClosed { channel_id });
    Ok(())
}
```

---

## Finding 4 — CRITICAL: Counter Overflow Causes ID Collision and Storage Clobber

**Location:** `create_client`, `open_connection`, `open_channel`

**Description:** All three counter increments use unchecked `+ 1`. When any counter reaches `u32::MAX` (4,294,967,295), the next increment wraps to `0`, causing the new entity to overwrite ID 0 in storage. All existing state (clients, connections, channels, sequence numbers) for that ID is silently destroyed.

```rust
// BEFORE — create_client
let client_id = IbcClientCounter::<T>::get();
IbcClientCounter::<T>::put(client_id + 1);

// AFTER — create_client
let client_id = IbcClientCounter::<T>::get();
let next_id = client_id.checked_add(1).ok_or(Error::<T>::ArithmeticOverflow)?;
IbcClientCounter::<T>::put(next_id);
```

```rust
// BEFORE — open_connection
let connection_id = IbcConnectionCounter::<T>::get();
IbcConnectionCounter::<T>::put(connection_id + 1);

// AFTER — open_connection
let connection_id = IbcConnectionCounter::<T>::get();
let next_id = connection_id.checked_add(1).ok_or(Error::<T>::ArithmeticOverflow)?;
IbcConnectionCounter::<T>::put(next_id);
```

```rust
// BEFORE — open_channel
let channel_id = IbcChannelCounter::<T>::get();
IbcChannelCounter::<T>::put(channel_id + 1);

// AFTER — open_channel
let channel_id = IbcChannelCounter::<T>::get();
let next_id = channel_id.checked_add(1).ok_or(Error::<T>::ArithmeticOverflow)?;
IbcChannelCounter::<T>::put(next_id);
```

Add to `Error<T>`:
```rust
ArithmeticOverflow,
```

---

## Finding 5 — HIGH: `IbcTotalTransfers` and `IbcTotalVolume` Overflow

**Location:** `transfer`

**Description:** Both statistics use unchecked arithmetic. `IbcTotalTransfers` (u64) overflows after ~1.8×10¹⁹ transfers and `IbcTotalVolume` (u128) overflows after sufficient token volume. In release builds without overflow checks, this silently resets counters to 0, corrupting protocol statistics.

```rust
// BEFORE
IbcTotalTransfers::<T>::put(IbcTotalTransfers::<T>::get() + 1);
IbcTotalVolume::<T>::put(IbcTotalVolume::<T>::get() + amount);

// AFTER
let new_transfers = IbcTotalTransfers::<T>::get()
    .checked_add(1)
    .ok_or(Error::<T>::ArithmeticOverflow)?;
IbcTotalTransfers::<T>::put(new_transfers);

let new_volume = IbcTotalVolume::<T>::get()
    .checked_add(amount)
    .ok_or(Error::<T>::ArithmeticOverflow)?;
IbcTotalVolume::<T>::put(new_volume);
```

---

## Finding 6 — HIGH: Timeout Calculation Overflows in `transfer`

**Location:** `transfer`

**Description:** The timeout is computed as `current_block + 1000`. If the block number conversion to u64 yields a value near `u64::MAX`, adding 1000 overflows. `unwrap_or(0)` also silently produces a zero block number, making every packet immediately timed out.

```rust
// BEFORE
let timeout: u64 = frame_system::Pallet::<T>::block_number()
    .try_into()
    .unwrap_or(0)
    + 1000;

// AFTER
let current_block: u64 = frame_system::Pallet::<T>::block_number()
    .try_into()
    .map_err(|_| Error::<T>::ArithmeticOverflow)?;

let timeout = current_block
    .checked_add(1000)
    .ok_or(Error::<T>::ArithmeticOverflow)?;
```

---

## Finding 7 — HIGH: `send_packet` — Sequence Overflow and Wrong Destination Channel

**Location:** `send_packet`

**Description:** Two bugs:
1. `sequence + 1` is unchecked and can overflow to 0, reusing sequence 0 and overwriting an existing packet.
2. `destination_channel` is set to `channel_id` (the **source** channel), which is incorrect. The destination channel on the counterparty chain is a different ID and must be provided by the caller or retrieved from the channel's `counterparty_channel_id` field.

```rust
// BEFORE
let sequence = IbcNextSequenceSend::<T>::get(channel_id);
IbcNextSequenceSend::<T>::insert(channel_id, sequence + 1);

let packet = Packet {
    sequence,
    source_port: source_port.clone(),
    source_channel: channel_id,
    destination_port: dest_port,
    destination_channel: channel_id, // BUG: should be counterparty channel
    data,
    timeout_height,
};

// AFTER
let sequence = IbcNextSequenceSend::<T>::get(channel_id);
let next_sequence = sequence.checked_add(1).ok_or(Error::<T>::ArithmeticOverflow)?;
IbcNextSequenceSend::<T>::insert(channel_id, next_sequence);

// Retrieve the counterparty channel ID from channel state
let dest_channel = channel
    .counterparty_channel_id
    .ok_or(Error::<T>::CounterpartyChannelNotSet)?;

let packet = Packet {
    sequence,
    source_port: source_port.clone(),
    source_channel: channel_id,
    destination_port: dest_port,
    destination_channel: dest_channel,
    data,
    timeout_height,
};
```

Add error:
```rust
CounterpartyChannelNotSet,
```

---

## Finding 8 — HIGH: `recv_packet` Does Not Verify Packet Commitment

**Location:** `recv_packet`

**Description:** `recv_packet` accepts a `sequence` number and marks it received, but never verifies that a corresponding packet with that sequence actually exists in `IbcPackets` or was committed on the source chain. The `_data` parameter is accepted but ignored. An attacker can call `recv_packet` with arbitrary sequence numbers to advance `IbcNextSequenceRecv` and permanently skip legitimate packets.

```rust
// BEFORE
pub fn recv_packet(
    origin: OriginFor<T>,
    channel_id: u32,
    sequence: u64,
    dest_port: Vec<u8>,
    _data: Vec<u8>,       // data silently ignored
) -> DispatchResult {
    let _who = ensure_signed(origin)?;
    let channel = IbcChannels::<T>::get(channel_id).ok_or(Error::<T>::ChannelNotFound)?;
    ensure!(channel.state == 3, Error::<T>::ChannelNotOpen);
    let expected_seq = IbcNextSequenceRecv::<T>::get(channel_id);
    ensure!(sequence == expected_seq, Error::<T>::InvalidSequence);
    IbcNextSequenceRecv::<T>::insert(channel_id, sequence + 1);
    // ...
}

// AFTER
pub fn recv_packet(
    origin: OriginFor<T>,
    channel_id: u32,
    sequence: u64,
    dest_port: Vec<u8>,
    data: Vec<u8>,
) -> DispatchResult {
    ensure_root(origin)?; // Only authorized relayers

    let channel = IbcChannels::<T>::get(channel_id).ok_or(Error::<T>::ChannelNotFound)?;
    ensure!(channel.state == 3, Error::<T>::ChannelNotOpen);

    // Verify packet exists (committed by sender on this chain or via proof)
    ensure!(
        IbcPackets::<T>::contains_key((channel_id, sequence)),
        Error::<T>::PacketNotFound
    );

    let expected_seq = IbcNextSequenceRecv::<T>::get(channel_id);
    ensure!(sequence == expected_seq, Error::<T>::InvalidSequence);

    let next_seq = sequence.checked_add(1).ok_or(Error::<T>::ArithmeticOverflow)?;
    IbcNextSequenceRecv::<T>::insert(channel_id, next_seq);

    // Verify data matches committed packet
    let stored_packet = IbcPackets::<T>::get((channel_id, sequence))
        .ok_or(Error::<T>::PacketNotFound)?;
    ensure!(stored_packet.data == data, Error::<T>::InvalidPacketData);

    Self::deposit_event(Event::PacketReceived {
        channel_id,
        sequence,
        dest_port,
    });
    Ok(())
}
```

Add errors:
```rust
PacketNotFound,
InvalidPacketData,
```

---

## Finding 9 — HIGH: `acknowledge_packet` Ack Sequence Not Correlated to Packet Sequence

**Location:** `acknowledge_packet`

**Description:** The `next_ack` counter is incremented regardless of the `sequence` argument passed in. If `sequence=5` is acknowledged but `next_ack=3`, the counter moves to 4 while sequence 5 is deleted. Sequences 3 and 4 can never be acknowledged. The ack counter is entirely decorrelated from actual packet sequences.

*(This is also covered in Finding 1's fix — included here as a distinct logical bug.)*

```rust
// BEFORE
IbcPackets::<T>::remove((channel_id, sequence));
let next_ack = IbcNextSequenceAck::<T>::get(channel_id);
IbcNextSequenceAck::<T>::insert(channel_id, next_ack + 1);
// next_ack is unrelated to `sequence`

// AFTER
let next_ack = IbcNextSequenceAck::<T>::get(channel_id);
// Enforce in-order acknowledgement
ensure!(sequence == next_ack, Error::<T>::InvalidSequence);
ensure!(
    IbcPackets::<T>::contains_key((channel_id, sequence)),
    Error::<T>::PacketNotFound
);
IbcPackets::<T>::remove((channel_id, sequence));
let new_next_ack = next_ack.checked_add(1).ok_or(Error::<T>::ArithmeticOverflow)?;
IbcNextSequenceAck::<T>::insert(channel_id, new_next_ack);
```

---

## Finding 10 — MEDIUM: `close_channel` Leaves Orphaned Packets in Storage

**Location:** `close_channel`

**Description:** When a channel is closed, all `IbcPackets` keyed to that `channel_id` remain in storage permanently. Sequence counters also remain. This is a storage leak that grows unboundedly and wastes state rent.

```rust
// AFTER close_channel — drain orphaned packets
// Note: only feasible if packet count is bounded; otherwise track
// sent/pending packet count per channel to enable safe iteration.

IbcChannels::<T>::mutate(channel_id, |ch| {
    if let Some(c) = ch {
        c.state = 4;
    }
});

// Remove sequence tracking for closed channel
IbcNextSequenceSend::<T>::remove(channel_id);
IbcNextSequenceRecv::<T>::remove(channel_id);
IbcNextSequenceAck::<T>::remove(channel_id);

// Packet cleanup should be handled via a bounded pending-packet
// counter + explicit close-with-refund extrinsic in production.
```

---

## Finding 11 — MEDIUM: `open_connection` Skips IBC Handshake

**Location:** `open_connection`

**Description:** A real IBC connection requires a 4-step handshake (`ConnOpenInit` → `ConnOpenTry` → `ConnOpenAck` → `ConnOpenConfirm`) with light client proof verification at each step. This implementation directly sets state to `3` (Open), bypassing all verification. Any user can instantly claim an open connection to any chain without cryptographic proof.

```rust
// BEFORE
let connection = ConnectionEnd {
    client_id,
    counterparty_client_id,
    state: 3, // Open — skips handshake
};

// AFTER (minimum viable fix — use Init state and separate confirm extrinsic)
let connection = ConnectionEnd {
    client_id,
    counterparty_client_id,
    state: 1, // Init only; Open requires counterparty proof via open_connection_confirm
};
```

---

## Finding 12 — MEDIUM: `open_channel` Skips IBC Channel Handshake

**Location:** `open_channel`

**Description:** Same pattern as Finding 11. IBC channels require `ChanOpenInit` → `ChanOpenTry` → `ChanOpenAck` → `ChanOpenConfirm`. Setting state directly to `3` (Open) means any user can fabricate open channels without counterparty confirmation.

```rust
// BEFORE
let channel = ChannelEnd {
    ordering,
    connection_id,
    state: 3, // Open — skips handshake
    counterparty_channel_id: None,
    port_id: port_id.clone(),
};

// AFTER
let channel = ChannelEnd {
    ordering,
    connection_id,
    state: 1, // Init; transitions to Open only after counterparty confirm extrinsic
    counterparty_channel_id: None,
    port_id: port_id.clone(),
};
```

---

## Finding 13 — LOW: Wrong Error Variant in `timeout_packet`

**Location:** `timeout_packet`

**Description:** When the packet is not found in storage, the error returned is `ChannelNotFound`, which is semantically wrong and misleads debugging.

```rust
// BEFORE
let packet =
    IbcPackets::<T>::get((channel_id, sequence)).ok_or(Error::<T>::ChannelNotFound)?;

// AFTER
let packet =
    IbcPackets::<T>::get((channel_id, sequence)).ok_or(Error::<T>::PacketNotFound)?;
```

---

## Consolidated New Error Variants Required

```rust
#[pallet::error]
pub enum Error<T> {
    ClientNotFound,
    ConnectionNotFound,
    ChannelNotFound,
    ChannelNotOpen,
    ConnectionNotOpen,
    ClientFrozen,
    InvalidSequence,
    PacketTimeout,
    PacketNotYetTimedOut,      // NEW: Finding 2
    PortIdTooLong,
    PacketDataTooLarge,
    PacketNotFound,             // NEW: Findings 1, 8, 9, 13
    ArithmeticOverflow,         // NEW: Findings 4, 5, 6, 7, 8, 9
    CounterpartyChannelNotSet,  // NEW: Finding 7
    InvalidPacketData,          // NEW: Finding 8
}
```