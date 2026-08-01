#!/usr/bin/env python3
"""Patch vm.js: Add stack depth limit + execution timeout"""

with open('/opt/verdis/app/dist/core/vm.js') as f:
    content = f.read()

# Fix: Add stack depth limit to StackVM constructor
old_ctor = """class StackVM {
    constructor(state) {
        this.gasLimit = 1000000;
        this.stack = [];
        this.state = state || new Map();
        this.events = [];
        this.pc = 0;
        this.halted = false;
        this.gasUsed = 0;
        this.gasLimit = 1000000;
        this.transientStorage = new Map();
    }"""

new_ctor = """class StackVM {
    constructor(state) {
        this.stack = [];
        this.state = state || new Map();
        this.events = [];
        this.pc = 0;
        this.halted = false;
        this.gasUsed = 0;
        this.gasLimit = 1000000;
        this.maxStackDepth = 1024;
        this.maxInstructionCount = 10000000;
        this.instructionCount = 0;
        this.transientStorage = new Map();
    }"""

if old_ctor in content:
    content = content.replace(old_ctor, new_ctor)
    print("1. Added stack depth + instruction limits to VM constructor")
else:
    print("1. ERROR: StackVM constructor not found")

# Fix: Add stack depth check in push()
old_push = """push(value) {
        this.stack.push(value);
    }"""

new_push = """push(value) {
        if (this.stack.length >= this.maxStackDepth) {
            throw new Error('Stack overflow: max depth ' + this.maxStackDepth + ' exceeded');
        }
        this.stack.push(value);
    }"""

if old_push in content:
    content = content.replace(old_push, new_push)
    print("2. Added stack overflow check in push()")
else:
    print("2. ERROR: push not found")

# Fix: Add instruction count check in run()
old_run = """run(bytecode) {
        this.pc = 0;
        this.halted = false;
        this.gasUsed = 0;
        while (this.pc < bytecode.length && !this.halted) {"""

new_run = """run(bytecode) {
        this.pc = 0;
        this.halted = false;
        this.gasUsed = 0;
        this.instructionCount = 0;
        while (this.pc < bytecode.length && !this.halted) {
            // Prevent infinite loops
            this.instructionCount++;
            if (this.instructionCount > this.maxInstructionCount) {
                return {
                    result: this.peek(),
                    events: this.events,
                    gasUsed: this.gasUsed,
                    error: 'Instruction limit exceeded: ' + this.maxInstructionCount,
                };
            }"""

if old_run in content:
    content = content.replace(old_run, new_run)
    print("3. Added instruction count limit in run()")
else:
    print("3. ERROR: run() not found")

with open('/opt/verdis/app/dist/core/vm.js', 'w') as f:
    f.write(content)
print("VM security patched successfully!")
