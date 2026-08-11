
// === P1 IBC SECURITY TESTS ===

/// Test: Non-root user cannot create IBC client
#[test]
fn test_unauthorized_client_creation_rejected() {
    new_test_ext().execute_with(|| {
        let acct = sp_core::crypto::AccountId32::from([0xff; 32]);
        frame_support::assert_noop!(
            Pallet::<Test>::create_client(
                frame_system::RawOrigin::Signed(acct).into(),
                1,
                100,
                86400
            ),
            sp_runtime::DispatchError::BadOrigin
        );
    });
}

/// Test: Non-root user cannot open IBC connection
#[test]
fn test_unauthorized_connection_opening_rejected() {
    new_test_ext().execute_with(|| {
        let acct = sp_core::crypto::AccountId32::from([0xff; 32]);
        assert_ok!(Pallet::<Test>::create_client(
            frame_system::RawOrigin::Root.into(),
            1,
            100,
            86400
        ));

        frame_support::assert_noop!(
            Pallet::<Test>::open_connection(
                frame_system::RawOrigin::Signed(acct).into(),
                0,
                1
            ),
            sp_runtime::DispatchError::BadOrigin
        );
    });
}

/// Test: Non-root user cannot open IBC channel
#[test]
fn test_unauthorized_channel_opening_rejected() {
    new_test_ext().execute_with(|| {
        let acct = sp_core::crypto::AccountId32::from([0xff; 32]);
        setup_chain();

        frame_support::assert_noop!(
            Pallet::<Test>::open_channel(
                frame_system::RawOrigin::Signed(acct).into(),
                0,
                1,
                b"transfer".to_vec()
            ),
            sp_runtime::DispatchError::BadOrigin
        );
    });
}

/// Test: Transfer to non-existent channel fails
#[test]
fn test_transfer_nonexistent_channel_rejected() {
    new_test_ext().execute_with(|| {
        let acct = sp_core::crypto::AccountId32::from([0xff; 32]);
        frame_support::assert_noop!(
            Pallet::<Test>::transfer(
                frame_system::RawOrigin::Signed(acct).into(),
                999,
                b"receiver".to_vec(),
                1000,
                b"VRS".to_vec()
            ),
            Error::<Test>::ChannelNotFound
        );
    });
}

/// Test: Transfer exceeding max amount fails
#[test]
fn test_transfer_exceeding_max_amount_rejected() {
    new_test_ext().execute_with(|| {
        let acct = sp_core::crypto::AccountId32::from([0xff; 32]);
        setup_chain();

        // MaxTransferAmount = 1_000_000_000_000_000
        frame_support::assert_noop!(
            Pallet::<Test>::transfer(
                frame_system::RawOrigin::Signed(acct).into(),
                0,
                b"receiver".to_vec(),
                2_000_000_000_000_000,
                b"VRS".to_vec()
            ),
            Error::<Test>::TransferAmountTooLarge
        );
    });
}

/// Test: Transfer with zero amount fails
#[test]
fn test_transfer_zero_amount_rejected() {
    new_test_ext().execute_with(|| {
        let acct = sp_core::crypto::AccountId32::from([0xff; 32]);
        setup_chain();

        frame_support::assert_noop!(
            Pallet::<Test>::transfer(
                frame_system::RawOrigin::Signed(acct).into(),
                0,
                b"receiver".to_vec(),
                0,
                b"VRS".to_vec()
            ),
            Error::<Test>::InsufficientBalance
        );
    });
}

/// Test: Send packet with data too large fails
#[test]
fn test_send_packet_data_too_large_rejected() {
    new_test_ext().execute_with(|| {
        let acct = sp_core::crypto::AccountId32::from([0xff; 32]);
        setup_chain();

        let large_data = vec![0u8; 2048]; // MaxPacketDataLen = 1024
        frame_support::assert_noop!(
            Pallet::<Test>::send_packet(
                frame_system::RawOrigin::Signed(acct).into(),
                0,
                b"transfer".to_vec(),
                b"transfer".to_vec(),
                large_data,
                10000,
                0
            ),
            Error::<Test>::PacketDataTooLarge
        );
    });
}

/// Test: Send packet with past timeout height fails
#[test]
fn test_send_packet_past_timeout_rejected() {
    new_test_ext().execute_with(|| {
        let acct = sp_core::crypto::AccountId32::from([0xff; 32]);
        setup_chain();

        // Current block is 1, timeout at 0 (past)
        frame_support::assert_noop!(
            Pallet::<Test>::send_packet(
                frame_system::RawOrigin::Signed(acct).into(),
                0,
                b"transfer".to_vec(),
                b"transfer".to_vec(),
                b"data".to_vec(),
                0,  // past timeout height
                0
            ),
            Error::<Test>::PacketTimeout
        );
    });
}

/// Test: Open channel with port ID too long fails
#[test]
fn test_open_channel_port_id_too_long_rejected() {
    new_test_ext().execute_with(|| {
        assert_ok!(Pallet::<Test>::create_client(
            frame_system::RawOrigin::Root.into(),
            1,
            100,
            86400
        ));
        assert_ok!(Pallet::<Test>::open_connection(
            frame_system::RawOrigin::Root.into(),
            0,
            1
        ));

        let long_port = vec![b'X'; 200]; // MaxPortIdLen = 128
        frame_support::assert_noop!(
            Pallet::<Test>::open_channel(
                frame_system::RawOrigin::Root.into(),
                0,
                1,
                long_port
            ),
            Error::<Test>::PortIdTooLong
        );
    });
}

/// Test: Open connection with non-existent client fails
#[test]
fn test_open_connection_nonexistent_client_rejected() {
    new_test_ext().execute_with(|| {
        frame_support::assert_noop!(
            Pallet::<Test>::open_connection(
                frame_system::RawOrigin::Root.into(),
                999,
                1
            ),
            Error::<Test>::ClientNotFound
        );
    });
}

/// Test: Open channel with non-existent connection fails
#[test]
fn test_open_channel_nonexistent_connection_rejected() {
    new_test_ext().execute_with(|| {
        frame_support::assert_noop!(
            Pallet::<Test>::open_channel(
                frame_system::RawOrigin::Root.into(),
                999,
                1,
                b"transfer".to_vec()
            ),
            Error::<Test>::ConnectionNotFound
        );
    });
}

/// Test: Open connection with frozen client fails
#[test]
fn test_open_connection_frozen_client_rejected() {
    new_test_ext().execute_with(|| {
        assert_ok!(Pallet::<Test>::create_client(
            frame_system::RawOrigin::Root.into(),
            1,
            100,
            86400
        ));

        // Freeze the client
        assert_ok!(Pallet::<Test>::freeze_client(
            frame_system::RawOrigin::Root.into(),
            0
        ));

        // Try to open connection on frozen client
        frame_support::assert_noop!(
            Pallet::<Test>::open_connection(
                frame_system::RawOrigin::Root.into(),
                0,
                1
            ),
            Error::<Test>::ClientFrozen
        );
    });
}

/// Test: Acknowledge non-existent packet fails
#[test]
fn test_acknowledge_nonexistent_packet_rejected() {
    new_test_ext().execute_with(|| {
        let acct = sp_core::crypto::AccountId32::from([0xff; 32]);
        setup_chain();

        frame_support::assert_noop!(
            Pallet::<Test>::acknowledge_packet(
                frame_system::RawOrigin::Signed(acct).into(),
                0,
                999
            ),
            Error::<Test>::PacketNotFound
        );
    });
}

/// Test: Timeout on non-existent packet fails
#[test]
fn test_timeout_nonexistent_packet_rejected() {
    new_test_ext().execute_with(|| {
        let acct = sp_core::crypto::AccountId32::from([0xff; 32]);
        setup_chain();

        frame_support::assert_noop!(
            Pallet::<Test>::timeout_packet(
                frame_system::RawOrigin::Signed(acct).into(),
                0,
                999
            ),
            Error::<Test>::PacketNotFound
        );
    });
}

/// Test: Close non-existent channel fails
#[test]
fn test_close_nonexistent_channel_rejected() {
    new_test_ext().execute_with(|| {
        let acct = sp_core::crypto::AccountId32::from([0xff; 32]);
        frame_support::assert_noop!(
            Pallet::<Test>::close_channel(
                frame_system::RawOrigin::Signed(acct).into(),
                999
            ),
            Error::<Test>::ChannelNotFound
        );
    });
}
