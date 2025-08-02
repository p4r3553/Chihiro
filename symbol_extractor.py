def extract_symbols(elf):
    symbols = []

    ELF_TYPE_MAP = {
        0: "NOTYPE",
        1: "OBJECT",
        2: "FUNC",
        3: "SECTION",
        4: "FILE",
        5: "COMMON",
        6: "TLS",
    }

    for section in elf.iter_sections():
        if not hasattr(section, 'iter_symbols'):
            continue

        for symbol in section.iter_symbols():
            sym_name = symbol.name

           
            try:
                sym_addr = symbol['st_value']
            except KeyError:
                sym_addr = 0

           
            try:
                sym_type_code = symbol['st_info']['type']
                sym_type = ELF_TYPE_MAP.get(sym_type_code, f"TYPE_{sym_type_code}")
            except Exception:
                sym_type = "UNKNOWN"

            if sym_name:
                symbols.append({
                    'name': sym_name,
                    'addr': sym_addr,
                    'type': sym_type
                })

    return symbols
