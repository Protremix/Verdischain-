import { OPCODES, StackVM, ContractManager, compileContract } from './core/vm';

function runTests() {
  console.log('--- Testing compileContract ---');
  const source = `
    // Simple test contract
    PUSH 5
    PUSH 10
    ADD
    LOG
    HALT
  `;

  const bytecode = compileContract(source);
  console.log('Compiled Bytecode:', bytecode);

  console.log('\n--- Testing StackVM ---');
  const vm = new StackVM();
  const res = vm.run(bytecode);
  console.log('VM Run Result:', res);
  console.assert(res.result === 15, 'Expected 5 + 10 = 15');
  console.assert(res.events.length === 1, 'Expected 1 LOG event');
  console.assert(res.events[0].data === 15, 'LOG data should be 15');

  console.log('\n--- Testing Loop and JUMPI in VM ---');
  const loopSource = `
    PUSH 0
    STORE counter

    LABEL loop
    LOAD counter
    PUSH 1
    ADD
    STORE counter
    LOAD counter
    PUSH 3
    LT
    JUMPI loop

    LOAD counter
    HALT
  `;

  const loopBytecode = compileContract(loopSource);
  console.log('Loop Bytecode:', loopBytecode);

  const loopVM = new StackVM();
  const loopRes = loopVM.run(loopBytecode);
  console.log('Loop VM Result:', loopRes);
  console.assert(loopRes.result === 3, `Expected counter = 3, got ${loopRes.result}`);

  console.log('\n--- Testing ContractManager ---');
  const manager = new ContractManager();
  const contract = manager.deploy('alice', 'TestContract', bytecode);
  console.log('Deployed Contract:', contract.id, contract.name);

  const execRes = manager.execute(contract.id, null);
  console.log('Contract Manager Execute Result:', execRes);
  console.assert(execRes.result === 15, 'Execution result should be 15');

  console.log('\n--- Testing StackVM Stack Operations (DUP, SWAP, SSTORE, SLOAD) ---');
  const stackSource = `
    PUSH 42
    DUP
    SSTORE key
    SLOAD key
    HALT
  `;
  const stackBytecode = compileContract(stackSource);
  const stackVM = new StackVM();
  const stackRes = stackVM.run(stackBytecode);
  console.log('Stack VM Result:', stackRes);
  console.assert(stackRes.result === 42, `Expected 42, got ${stackRes.result}`);

  console.log('\nALL VM TESTS PASSED SUCCESSFULLY!');
}

runTests();
