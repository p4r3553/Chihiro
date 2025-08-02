def print_binary_info(elf):
    print("\n[+] ELF File Info:")
    header = elf.header

    elfclass = header['e_ident']['EI_CLASS']
    print(f"    Format        : {'ELF64' if elfclass == 'ELFCLASS64' else 'ELF32'}")

    machine = header['e_machine']
    print(f"    Architecture  : {machine}")

    endian = header['e_ident']['EI_DATA']
    print(f"    Endianness    : {'Little' if endian == 'ELFDATA2LSB' else 'Big'}")

    entry = header['e_entry']
    print(f"    Entry point   : 0x{entry:x}")

    print(f"    Sections      : {elf.num_sections()}")
    print("    Section names :")
    for section in elf.iter_sections():
        print(f"      - {section.name}")
