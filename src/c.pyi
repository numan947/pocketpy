from typing import overload

def malloc(size: int) -> 'void_p': ...
def free(ptr: 'void_p') -> None: ...
def sizeof(type: str) -> int: ...
def refl(name: str) -> '_refl': ...
def memset(ptr: 'void_p', value: int, size: int) -> None: ...
def memcpy(dst: 'void_p', src: 'void_p', size: int) -> None: ...

class _refl:
    def __call__(self) -> 'struct': ...
    def __getitem__(self, key: str) -> int: ...
    def name(self) -> str: ...
    def size(self) -> int: ...

class void_p:
    def __add__(self, i: int) -> 'void_p': ...
    def __sub__(self, i: int) -> 'void_p': ...
    def __eq__(self, other: 'void_p') -> bool: ...
    def __ne__(self, other: 'void_p') -> bool: ...
    def offset(self, i: int) -> 'void_p': ...

    def hex(self) -> str: ...
    @staticmethod
    def from_hex(s: str) -> 'void_p': ...

    def read_char(self) -> int: ...
    def read_uchar(self) -> int: ...
    def read_short(self) -> int: ...
    def read_ushort(self) -> int: ...
    def read_int(self) -> int: ...
    def read_uint(self) -> int: ...
    def read_long(self) -> int: ...
    def read_ulong(self) -> int: ...
    def read_longlong(self) -> int: ...
    def read_ulonglong(self) -> int: ...
    def read_float(self) -> float: ...
    def read_double(self) -> float: ...
    def read_bool(self) -> bool: ...
    def read_void_p(self) -> 'void_p': ...
    def read_bytes(self, size: int) -> bytes: ...
    def read_struct(self, type: str) -> 'struct': ...

    def write_char(self, value: int) -> None: ...
    def write_uchar(self, value: int) -> None: ...
    def write_short(self, value: int) -> None: ...
    def write_ushort(self, value: int) -> None: ...
    def write_int(self, value: int) -> None: ...
    def write_uint(self, value: int) -> None: ...
    def write_long(self, value: int) -> None: ...
    def write_ulong(self, value: int) -> None: ...
    def write_longlong(self, value: int) -> None: ...
    def write_ulonglong(self, value: int) -> None: ...
    def write_float(self, value: float) -> None: ...
    def write_double(self, value: float) -> None: ...
    def write_bool(self, value: bool) -> None: ...
    def write_void_p(self, value: 'void_p') -> None: ...
    def write_bytes(self, value: bytes) -> None: ...
    def write_struct(self, value: 'struct') -> None: ...

    def get_base_offset(self) -> int: ...
    @overload
    def set_base_offset(self, offset: int) -> None: ...
    @overload
    def set_base_offset(self, offset: str) -> None: ...
    
class struct:
    def addr(self) -> 'void_p': ...
    def copy(self) -> 'struct': ...
    def size(self) -> int: ...
    def __eq__(self, other: 'struct') -> bool: ...
    def __ne__(self, other: 'struct') -> bool: ...
