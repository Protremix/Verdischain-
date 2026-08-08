#!/usr/bin/env python3
"""Fix DEX pool bricking: allow re-initialization when total_lp == 0."""

FILE = '/opt/verdis-chain-rust/pallets/amm-dex/src/lib.rs'

with open(FILE, 'r') as f:
    content = f.read()

# Fix add_liquidity (native pools) — replace the block that checks reserves > 0
old_block_1 = """            ensure!(amount_a > BalanceOf::<T>::zero(), Error::<T>::ZeroAmount);
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

            T::Currency::reserve(&who, amount_a)?;
            T::Currency::reserve(&who, amount_b)?;

            pool.reserve_a = pool.reserve_a.checked_add(&amount_a)
                .ok_or(Error::<T>::ArithmeticOverflow)?;
            pool.reserve_b = pool.reserve_b.checked_add(&amount_b)
                .ok_or(Error::<T>::ArithmeticOverflow)?;
            pool.total_lp = pool.total_lp.checked_add(&lp_minted)
                .ok_or(Error::<T>::ArithmeticOverflow)?;"""

new_block_1 = """            ensure!(amount_a > BalanceOf::<T>::zero(), Error::<T>::ZeroAmount);
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

            T::Currency::reserve(&who, amount_a)?;
            T::Currency::reserve(&who, amount_b)?;

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

if old_block_1 in content:
    content = content.replace(old_block_1, new_block_1)
    print("✓ Fixed add_liquidity pool bricking")
else:
    print("✗ Could not find add_liquidity block to replace")
    # Try to find a partial match
    import re
    matches = re.findall(r'ensure!\(pool\.reserve_a.*?InsufficientLiquidity\);', content)
    for m in matches:
        print(f"  Found: {m[:80]}...")

# Also fix add_token_liquidity — similar pattern
old_block_2 = """            ensure!(amount_a > BalanceOf::<T>::zero(), Error::<T>::ZeroAmount);
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

            T::Currency::reserve(&who, amount_a)?;
            T::Currency::reserve(&who, amount_b)?;

            pool.reserve_a = pool.reserve_a.checked_add(&amount_a)
                .ok_or(Error::<T>::ArithmeticOverflow)?;
            pool.reserve_b = pool.reserve_b.checked_add(&amount_b)
                .ok_or(Error::<T>::ArithmeticOverflow)?;
            pool.total_lp = pool.total_lp.checked_add(&lp_minted)
                .ok_or(Error::<T>::ArithmeticOverflow)?;"""

new_block_2 = """            ensure!(amount_a > BalanceOf::<T>::zero(), Error::<T>::ZeroAmount);
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

            T::Currency::reserve(&who, amount_a)?;
            T::Currency::reserve(&who, amount_b)?;

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

if old_block_2 in content:
    content = content.replace(old_block_2, new_block_2)
    print("✓ Fixed add_token_liquidity pool bricking")
else:
    print("✗ Could not find add_token_liquidity block (may already be fixed by first replace)")

with open(FILE, 'w') as f:
    f.write(content)

print("Done")
