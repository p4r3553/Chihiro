from capstone import Cs, CS_ARCH_X86, CS_MODE_64

def disassemble(code, addr):
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    instructions = []
    for i in md.disasm(code, addr):
        instructions.append({
            'address': i.address,
            'mnemonic': i.mnemonic,
            'op_str': i.op_str
        })
    return instructions
