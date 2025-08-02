import networkx as nx

def build_cfg(instructions):
    cfg = nx.DiGraph()
    jump_mnemonics = (
        "jmp", "je", "jne", "jg", "jl", "jz", "jnz", "ja", "jb", "call"
    )
    conditional_jumps = (
        "je", "jne", "jg", "jl", "jz", "jnz", "ja", "jb"
    )

    jump_targets = {
        int(instr["op_str"], 16)
        for instr in instructions
        if instr["mnemonic"].startswith(jump_mnemonics)
        and instr.get("op_str", "").startswith("0x")
    }

    block_starts = set(jump_targets)
    for i, instr in enumerate(instructions[:-1]):
        if instr["mnemonic"].startswith(jump_mnemonics) or instr["mnemonic"].startswith("ret"):
            block_starts.add(instructions[i + 1]["address"])
    block_starts.add(instructions[0]["address"])  

    blocks = {}
    current_block = []

    for instr in instructions:
        addr = instr["address"]

        if addr in block_starts and current_block:
            blocks[current_block[0]["address"]] = current_block
            current_block = []

        current_block.append(instr)

        if instr["mnemonic"].startswith(("jmp", "ret")):
            blocks[current_block[0]["address"]] = current_block
            current_block = []

    if current_block:
        blocks[current_block[0]["address"]] = current_block

    for start_addr, instrs in blocks.items():
        cfg.add_node(start_addr, instructions=instrs)

    block_starts_sorted = sorted(blocks)
    addr_to_block_start = {
        instr["address"]: blk_start
        for blk_start, instrs in blocks.items()
        for instr in instrs
    }

    for i, start in enumerate(block_starts_sorted):
        block = blocks[start]
        last_instr = block[-1]
        mnem = last_instr["mnemonic"]
        op = last_instr.get("op_str", "")

        if mnem.startswith("jmp") and op.startswith("0x"):
            tgt = int(op, 16)
            tgt_blk = addr_to_block_start.get(tgt)
            if tgt_blk:
                cfg.add_edge(start, tgt_blk)

        elif mnem.startswith(conditional_jumps):
            if op.startswith("0x"):
                tgt = int(op, 16)
                tgt_blk = addr_to_block_start.get(tgt)
                if tgt_blk:
                    cfg.add_edge(start, tgt_blk)
            if i + 1 < len(block_starts_sorted):
                cfg.add_edge(start, block_starts_sorted[i + 1])

        elif mnem.startswith("call"):
            if i + 1 < len(block_starts_sorted):
                cfg.add_edge(start, block_starts_sorted[i + 1])

        elif not mnem.startswith("ret"):
            if i + 1 < len(block_starts_sorted):
                cfg.add_edge(start, block_starts_sorted[i + 1])

    return cfg
