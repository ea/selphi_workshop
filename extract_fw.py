import sys
import struct
import os

def readString(f):
	s = ""
	while True:
		c = f.read(1)
		if c == b'\x00':
			return s
		else:
			s+=c.decode('ascii')


def main():
	f = open(sys.argv[1],"rb")
	a = f.read(4)
	a = struct.unpack("I",a)[0]
	b = f.read(4)
	b = struct.unpack("I",b)[0]
	print(hex(a))
	print(hex(b))
	jumped = b""
	if a ^ b != 0xFFFFFFFF:
		print("bad flash")
		return 0
	offset = 8
	for step in range(a):
		f.seek(offset)
		t = f.read(4)
		t = struct.unpack("I",t)[0]
		#print("... ",hex(t))
		if t & 0x1000000:
			offset += 0x10
			#print("jumping 0x12")
			jumped += f.read(0xc)
		elif t > 0xf003ffff:
			offset += 8
			jumped += f.read(3)
			#print("jumping 8")
		else: 
			#print("jumping 5")
			jumped1 = f.read(1)
			jumped2 = f.read(4)
			#print(jumped1,"0x%x"%int.from_bytes(jumped2,"little"))
			jumped +=  jumped2
			offset += 5
	boot_fw_offset = offset+12
	print("boot firmware @", offset+12)
	#print(jumped)
	#f1 = open("jumped", "wb")
	#f1.write(jumped)
	#f1.close()
	f.seek(boot_fw_offset)
	f.seek(boot_fw_offset+0x10);
	romtab_offset = f.read(4)
	romtab_offset = struct.unpack("I",romtab_offset)[0]
	print("romtab offset ", hex(romtab_offset))
	f.seek(romtab_offset)
	romtab_header = f.read(0x2c)
	romtab_magic,rom_version,unk1,num_items,fw_idx,fw_memory_address,romtab_size,unk4,unk5,unk6,unk7 = struct.unpack("IIIIIIIIIII",romtab_header)
	print("romtab:\n \tmagic: %d"
		  "\n\trom_version: 0x%x\n\tunk1: 0x%x\n\tnum_items: %d\n\t"
		  "fw_idx: 0x%x\n\tfw_memory_address: 0x%x\n\tromtab_size: %d\n\t"
		  "rom_size: 0x%x\n\tunk5: 0x%x\n\tunk6: 0x%x\n\tunk7: 0x%x\n\t"%(romtab_magic,
		  			rom_version,unk1,num_items,
		  			fw_idx,fw_memory_address,
		  			romtab_size,unk4,unk5,unk6,unk7))
	"""
	f.seek(romtab_offset + romtab_size)
	string_table_tag = f.read(4)
	string_table_tag = struct.unpack("I",string_table_tag)[0]
	print(hex(string_table_tag))
	string_table_size = f.read(4)
	string_table_size = struct.unpack("I",string_table_size)[0]
	print(hex(string_table_size))
	"""
	strtab = []
	f.seek(romtab_offset+0x28+12*num_items)
	for i in range(num_items):
		strtab.append(readString(f))
	f.seek(romtab_offset+0x28)
	modules = []

	for i in range(num_items):
		d = f.read(12)
		addr,size, flags = struct.unpack("III",d)
		print("\t 0x%x 0x%x 0x%x %s"%(addr,size, flags,strtab[i]))
		module = {'addr':addr&0x7fffff,"size":size, flags:flags,"name":strtab[i]}
		modules.append(module)
	
	for m in modules:
		print("writing ",m['name'])
		f.seek(m['addr'])
		data = f.read(m['size'])
		f1 = open(os.path.join("flash_dump",m['name']),"wb")
		f1.write(data)
		f1.close()
	

if __name__ == '__main__':
	main()
