def find_xrefs(instructions, target_addr):
    xrefs = []
    for instr in instructions:
        if str(hex(target_addr)) in instr['op_str']:
            xrefs.append(instr['address'])
    return xrefs
