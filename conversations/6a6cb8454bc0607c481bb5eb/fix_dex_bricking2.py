#!/usr/bin/env python3
"""Fix add_token_liquidity pool bricking."""

FILE = '/opt/verdis-chain-rust/pallets/amm-dex/src/lib.rs'

with open(FILE, 'r') as f:
    content = f.read()

old_block = """            ensure!(amount_a > BalanceOf::<T>::zero(), Error::<T>::ZeroAmount);
            ensure!(amount_b > BalanceOf::<T>::zero(), Error::<T>::ZeroAmount);

            ensure!(pool.reserve_a > BalanceOf::<T>::zero(), Error::<T>::InsufficientLiquidity);
            ensure!(pool.reserve_b > BalanceOf::<T>::zero(), Error::<T>::InsufficientLiquidity);
            let lp_a = pool.total_lp.checked_mul(&amount_a)
                .ok_or(Error::<T>::ArithmeticOverflow)?
                / pool.reserve_a;
            let lp_b = pool.total_lp.checked_mul(&amount_b)
                .ok_or(Error::<T>::ArithmeticOverflow)?
                / pool.reserve_b;
            let lp_minted = lp_a.min(lp_b);
            ensure!(
                lp_minted > BalanceOf::<T>::zero(),
                Error::<T>::InsufficientAmount
            );

            ensure!(
                T::TokenHandler::has_balance(&pool.asset_a, &who, amount_a),
                Error::<T>::InsufficientLiquidityBalance
            );
            ensure!(
                T::TokenHandler::has_balance(&pool.asset_b, &who, amount_b),
                Error::<T>::InsufficientLiquidityBalance
            );

            let dex_account: T::AccountId = T::PalletId::get().into_account_truncating();
            T::TokenHandler::transfer(&pool.asset_a, &who, &dex_account, amount_a)?;
            T::TokenHandler::transfer(&pool.asset_b, &who, &dex_account, amount_b)?;

            pool.reserve_a = pool.reserve_a.checked_add(&amount_a)
                .ok_or(Error::<T>::ArithmeticOverflow)?;
            pool.reserve_b = pool.reserve_b.checked_add(&amount_b)
                .ok_or(Error::<T>::ArithmeticOverflow)?;
            pool.total_lp = pool.total_lp.checked_add(&lp_minted)
                .ok_or(Error::<T>::ArithmeticOverflow)?;"""

new_block = """            ensure!(amount_a > BalanceOf::<T>::zero(), Error::<T>::ZeroAmount);
            ensure!(amount_b > BalanceOf::<T>::zero(), Error::<T>::ZeroAmount);

            let lp_minted = if pool.total_lp == BalanceOf::<T>::zero() {
                // Re-initialize empty pool (prevents pool bricking)
                let product = amount_a.checked_mul(&amount_b)
                    .ok_or(Error::<T>::ArithmeticOverflow)?;
                product.integer_sqrt()
            } else {
                ensure!(pool.reserve_a > BalanceOf::<T>::zero(), Error::<T>::InsufficientLiquidity);
                ensure!(pool.reserve_b > BalanceOf::<T>::zero(), Error::<T>::InsufficientLiquidity);
                let lp_a = pool.total_lp.checked_mul(&amount_a)
                    .ok_or(Error::<T>::ArithmeticOverflow)?
                    / pool.reserve_a;
                let lp_b = pool.total_lp.checked_mul(&amount_b)
                    .ok_or(Error::<T>::ArithmeticOverflow)?
                    / pool.reserve_b;
                let lp = lp_a.min(lp_b);
                ensure!(
                    lp > BalanceOf::<T>::zero(),
                    Error::<T>::InsufficientAmount
                );
                lp
            };

            ensure!(
                T::TokenHandler::has_balance(&pool.asset_a, &who, amount_a),
                Error::<T>::InsufficientLiquidityBalance
            );
            ensure!(
                T::TokenHandler::has_balance(&pool.asset_b, &who, amount_b),
                Error::<T>::InsufficientLiquidityBalance
            );

            let dex_account: T::AccountId = T::PalletId::get().into_account_truncating();
            T::TokenHandler::transfer(&pool.asset_a, &who, &dex_account, amount_a)?;
            T::TokenHandler::transfer(&pool.asset_b, &who, &dex_account, amount_b)?;

            if pool.total_lp == BalanceOf::<T>::zero() {
                pool.reserve_a = amount_a;
                pool.reserve_b = amount_b;
            } else {
                pool.reserve_a = pool.reserve_a.checked_add(&amount_a)
                    .ok_or(Error::<T>::ArithmeticOverflow)?;
                pool.reserve_b = pool.reserve_b.checked_add(&amount_b)
                    .ok_or(Error::<T>::ArithmeticOverflow)?;
            }
            pool.total_lp = pool.total_lp.checked_add(&lp_minted)
                .ok_or(Error::<T>::ArithmeticOverflow)?;"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open(FILE, 'w') as f:
        f.write(content)
    print("✓ Fixed add_token_liquidity pool bricking")
else:
    print("✗ Pattern not found")
