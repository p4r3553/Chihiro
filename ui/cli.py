import argparse
import sys
from binary_loader import load_binary
from disassembler import disassemble
from string_extractor import extract_ascii_strings
from symbol_extractor import extract_symbols
from binary_info import print_binary_info
from utils.helpers import hex_dump

from graph.rodata_extractor import extract_rodata
from graph.cfg_builder import build_cfg
from graph.cfg_visualizer import visualize_cfg

def run_cli():
    parser = argparse.ArgumentParser(description="Chihiro - Binary Reverse Engineering CLI")
    parser.add_argument("binary", help="Path to binary file (ELF)")
    parser.add_argument("--disasm", action="store_true", help="Disassemble the .text section")
    parser.add_argument("--strings", action="store_true", help="Extract ASCII strings from .text")
    parser.add_argument("--hex", action="store_true", help="Show hex dump of the .text section")
    parser.add_argument("--info", action="store_true", help="Show ELF binary metadata")
    parser.add_argument("--symbols", action="store_true", help="Show symbol table (functions, objects, etc.)")
    parser.add_argument("--funcs-only", action="store_true", help="Show only function symbols")
    parser.add_argument("--rodata", action="store_true", help="Extract strings from .rodata section")
    parser.add_argument("--cfg", action="store_true", help="Visualize the control flow graph of .text")

    args = parser.parse_args()

    try:
        elf, file_obj = load_binary(args.binary)
    except Exception as e:
        print(f"[!] Failed to load binary: {e}")
        sys.exit(1)

    try:
        
        if args.info:
            print_binary_info(elf)

        
        if args.symbols:
            print("\n[+] Symbol Table:")
            symbols = extract_symbols(elf)
            for sym in symbols:
                if args.funcs_only and sym['type'] != "FUNC":
                    continue
                print(f"  0x{sym['addr']:08x}  {sym['type']:<15}  {sym['name']}")

        if args.disasm or args.strings or args.hex or args.cfg:
            text = elf.get_section_by_name('.text')
            if not text:
                print("[!] .text section not found in binary.")
                sys.exit(1)

            code = text.data()
            addr = text['sh_addr']

            if args.disasm:
                print("\n[+] Disassembly of .text:")
                for instr in disassemble(code, addr):
                    print(f"0x{instr['address']:x}: {instr['mnemonic']} {instr['op_str']}")

            if args.strings:
                print("\n[+] Extracted ASCII Strings from .text:")
                strings = extract_ascii_strings(code)
                for s in strings:
                    try:
                        print(s.decode('utf-8', errors='ignore'))
                    except Exception:
                        continue

            if args.hex:
                print("\n[+] Hex Dump of .text section:")
                print(hex_dump(code))

            if args.cfg:
                print("\n[+] Visualizing Control Flow Graph...")
                instructions = disassemble(code, addr)
                cfg = build_cfg(instructions)
                visualize_cfg(cfg)

      
        if args.rodata:
            print("\n[+] Strings from .rodata:")
            strings = extract_rodata(elf)
            for s in strings:
                print(f"  {s}")

    finally:
        file_obj.close()
if __name__ == "__main__":
    run_cli()
