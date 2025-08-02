from elftools.elf.elffile import ELFFile

def load_binary(path):
    f = open(path, 'rb')  
    elffile = ELFFile(f)
    return elffile, f 