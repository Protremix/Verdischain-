# Как задеплоить смарт-контракт на Verdis Chain

Документ описывает **фактическое** состояние на 2026-09-08, проверенное живыми запросами.
Там, где функциональность ещё не открыта пользователям, это сказано прямо.

---

## Коротко: два пути, и они не равнозначны

| | **ink!** (Rust) | **Solidity** (EVM) |
|---|---|---|
| Где работает | 🟢 **мейннет, сейчас** | 🟡 тестнет, порт закрыт извне |
| Кошелёк | наш Verdis Wallet | MetaMask для подписи |
| Адрес | `ki…` | `0x…` |
| Балансов | **один** | два, пока нет связки |
| Деплой | из кошелька / CLI | Remix в браузере |

**Если контракт нужен сегодня и на мейннете — только ink!.**

---

## Путь 1: ink! — работает на мейннете прямо сейчас

Проверено на мейннете (блок 65548):

```
Contracts.instantiate_with_code   доступен любому ki-аккаунту
живой контракт  kiYEc1bsNd1fAM7gKEjXrquXqYfEui4u31jdmPz9d3eGT1mUq
задеплоил       kiWreuiTEbX6nrXW3xuCQMeoCaEzgMBw8WCvXgk2ftD7yEBKG (блок 58442)
залог за код    1.7172 VRDX
DepositPerByte  0.001 VRDX      MaxCodeLen 125 952 байт
```

### Шаги

1. **Установить инструменты**
   ```bash
   cargo install --force --locked cargo-contract
   rustup target add wasm32-unknown-unknown
   ```

2. **Создать и собрать контракт**
   ```bash
   cargo contract new my_token
   cd my_token
   cargo contract build --release
   ```
   На выходе `target/ink/my_token.contract`.

3. **Задеплоить**
   ```bash
   cargo contract instantiate \
     --constructor new \
     --args 1000000 \
     --suri "<ваша seed-фраза>" \
     --url wss://rpc.verdischain.com \
     --execute
   ```
   Либо через Polkadot-JS Apps → Developer → Contracts, подключившись к
   `wss://rpc.verdischain.com`.

4. **Что дальше**
   Адрес контракта — обычный `ki…`. Вызовы подписываются вашим Verdis-кошельком.
   **Один адрес, один баланс, MetaMask не нужен вообще.**

### Что нужно знать про залог

Залог за хранение (`DepositPerByte` 0.001 VRDX за байт) **резервируется, а не тратится**.
Он возвращается при удалении контракта. Это не комиссия.

---

## Путь 2: Solidity через MetaMask

### ⚠️ Текущий статус: НЕ ДОСТУПНО ИЗВНЕ

Проверено:

```
rpc.verdischain.com  → eth_chainId → -32601 Method not found   (мейннет, EVM не развёрнут)
ws.verdischain.com   → 502 Bad Gateway
тестнет 9933-9938    → только 127.0.0.1, наружу не открыты
```

EVM **работает на тестнете** (chainId 414, контракт задеплоен, 19/19 проверок), но публичного
эндпоинта пока нет. Порядок открытия: публичный тестнет-RPC → аудит Halborn → мейннет.

### Когда откроется — параметры сети для MetaMask

```
Network name      Verdis Chain
RPC URL           https://rpc.verdischain.com     (будет testnet-rpc для тестнета)
Chain ID          414
Currency symbol   VRDX
Block explorer    https://explorer.verdischain.com
```

**Chain ID 414 выбран не случайно.** 909 занят в публичном реестре `chainid.network`
(Portal Fantasy Chain) — кошелёк пользователя, у которого уже добавлена та сеть, отверг бы Verdis.

### 🚨 Про баланс в MetaMask: важное предупреждение

MetaMask **официально не поддерживает** нативные токены с decimals ≠ 18.
Дословно из их документации:

> «MetaMask does not yet support chains with native currencies that do not have 18 decimals»

Баг [#15168](https://github.com/MetaMask/metamask-extension/issues/15168) открыт с июля 2022.
У VRDX **9 decimals**, поэтому **MetaMask покажет баланс в 10⁹ раз меньше реального**.

Это ограничение внутри MetaMask, не в нашей цепи. Наш эксплорер и наш кошелёк показывают
правильную сумму. Проверять баланс следует в `explorer.verdischain.com`.

### Шаги деплоя

1. **Добавить сеть** в MetaMask по параметрам выше.

2. **Получить VRDX.** На тестнете — `faucet.verdischain.com`.

3. **Открыть [remix.ethereum.org](https://remix.ethereum.org)**, вставить контракт,
   скомпилировать (Solidity 0.8.x).

4. **Deploy** → Environment: *Injected Provider — MetaMask* → Deploy → подписать.

Измеренная стоимость на тестнете:

```
деплой контракта   542 412 газа = ~8.31 VRDX
вызов increment()   84 912 газа = 0.8491 VRDX
обычный перевод     21 000 газа = 0.3216 VRDX
gasPrice            20 000 raw  = 0.00002 VRDX
```

Отношение «деплой / перевод» = **25.8×** — ровно как на Ethereum, Polygon, BNB, Base.
Проверено опросом их публичных RPC.

---

## 🚨 Главное, что обязан знать пользователь MetaMask СЕГОДНЯ

### У вас будет ДВА адреса и ДВА баланса

```
MetaMask:        0x70997970C51812dc3A010C7d01b50e0d17dc79C8
скрытый двойник: kib2nTbjUfLcnkwt3bmyiLVpZY2fd6oFLn2LG9G5PtXpobVcc
ваш Verdis-кошелёк: совершенно другой ki-адрес
```

Цепь превращает ваш `0x`-адрес в `ki`-аккаунт через `blake2("evm:" + адрес)`.
Это **односторонний хеш**: `0x → ki` вычисляется, `ki → 0x` — **невозможно**.

### Чего делать НЕЛЬЗЯ

**❌ Не отправляйте VRDX из MetaMask на свой `ki`-адрес.** Проверено на тестнете:

```
отправил 100 VRDX на первые 20 байт публичного ключа кошелька
status 0x1 — транзакция прошла
деньги легли на  kiaDUSjXCGyh82AtFSwZNMCfnrtz4xuVdAQYDDQz9XHrG97Mp
кошелёк-получатель НЕ ИЗМЕНИЛСЯ
```

**100 VRDX оказались на аккаунте, к которому нет приватного ключа ни у кого.**
Не у вас, не у нас — ни у кого. Восстановить нельзя.

**❌ Не удаляйте seed-фразу MetaMask.** Пока нет связки адресов, это **единственный**
способ распоряжаться средствами на EVM-стороне.

**❌ Не рассчитывайте на `EVM::withdraw`.** В рантайме стоит
`WithdrawOrigin = EnsureAddressTruncated`, что требует совпадения первых 20 байт
`ki`-аккаунта с EVM-адресом. У обычного кошелька они не совпадают.

### Что делать ПРАВИЛЬНО

- Держите средства для EVM **на MetaMask-адресе**, работайте с ними оттуда
- Проверяйте баланс в `explorer.verdischain.com`, а не в MetaMask (decimals)
- Для стейкинга и голосования используйте **Verdis-кошелёк и `ki`-аккаунт**
- ED = **1 VRDX**: перевод меньше этой суммы ревертится, и последний 1 VRDX
  с EVM-аккаунта не потратить (`Preservation::Preserve` в `pallet-evm`)

---

## Что изменится после связки адресов

Готовится палета `verdis-account-link`. После неё:

```
СЕЙЧАС:  MetaMask 0x7099… → blake2 → kib2nTbj… (скрытый, ключа нет)
         ваш кошелёк kibE5Qzs… — отдельно
         ДВА БАЛАНСА

ПОСЛЕ:   MetaMask 0x7099… → таблица связи → ваш kibE5Qzs…
         ОДИН БАЛАНС
```

Пользователь **один раз** подписывает в MetaMask подтверждение владения (EIP-712), и:

- ✅ баланс **один** — пришло в MetaMask, сразу видно и тратится в Verdis-кошельке
- ✅ MetaMask нужен **только для подписи деплоя**, дальше можно про него забыть
- ✅ стейкинг и голосование — с того же баланса
- ✅ ничего переводить не надо

Адрес по-прежнему отображается в двух форматах (`ki…` для Verdis, `0x…` для MetaMask) —
как один телефонный номер в двух записях. Но **деньги одни**.

---

## Порядок открытия EVM

1. ✅ EVM собран, `eth_chainId` = 414, Solidity задеплоен на тестнете
2. ⏳ палета связывания адресов
3. ⏳ публичный тестнет-RPC для MetaMask
4. ⏳ код-фриз
5. ⏳ аудит Halborn — **без единой находки**
6. ⏳ раскатка бинарей на 21 валидатор мейннета, по одному
7. ⏳ `set_code` на мейннете

**Шаг 6 нельзя пропустить:** EVM-рантайм требует 42 host-функции против 40 текущих.
`set_code` до раскатки бинарей остановит цепь необратимо.

---

## Куда смотреть

- Эксплорер: `https://explorer.verdischain.com`
- Кошелёк: `https://wallet.verdischain.com`
- Faucet (тестнет): `https://faucet.verdischain.com`
- RPC мейннета: `wss://rpc.verdischain.com` (Substrate, без EVM)
- Исходники: `https://github.com/Protremix/Verdischain-`
