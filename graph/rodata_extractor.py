def extract_rodata(elf):
    rodata_section = elf.get_section_by_name('.rodata')
    if not rodata_section:
        print("[!] .rodata section not found.")
        return []

    data = rodata_section.data()
    strings = []
    current = b""

    for byte in data:
        if 32 <= byte <= 126:
            current += bytes([byte])
        else:
            if len(current) >= 4:
                strings.append(current.decode(errors='ignore'))
            current = b""
    if len(current) >= 4:
        strings.append(current.decode(errors='ignore'))

    return strings
