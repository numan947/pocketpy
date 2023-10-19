import json
import builtins

_BASIC_TYPES = [int, float, str, bool, type(None)]
_MOD_T_SEP = "@"

def _find_class(path: str):
    if _MOD_T_SEP not in path:
        return builtins.__dict__[path]
    modpath, name = path.split(_MOD_T_SEP)
    return __import__(modpath).__dict__[name]

def _find__new__(cls):
    while cls is not None:
        d = cls.__dict__
        if "__new__" in d:
            return d["__new__"]
        cls = cls.__base__
    assert False

class _Pickler:
    def __init__(self, obj) -> None:
        self.obj = obj
        self.raw_memo = {}  # id -> int
        self.memo = []      # int -> object

    def _type_id(self, o: type):
        assert type(o) is type
        name = o.__name__
        mod = o.__module__
        if mod is not None:
            name = mod.__path__ + _MOD_T_SEP + name
        return name

    def wrap(self, o):
        if type(o) in _BASIC_TYPES:
            return o
        if type(o) is type:
            return ["type", self._type_id(o)]

        index = self.raw_memo.get(id(o), None)
        if index is not None:
            return [index]
        
        ret = []
        index = len(self.memo)
        self.memo.append(ret)
        self.raw_memo[id(o)] = index

        if type(o) is tuple:
            ret.append("tuple")
            ret.append([self.wrap(i) for i in o])
            return [index]
        if type(o) is bytes:
            ret.append("bytes")
            ret.append([o[j] for j in range(len(o))])
            return [index]

        if type(o) is list:
            ret.append("list")
            ret.append([self.wrap(i) for i in o])
            return [index]
        if type(o) is dict:
            ret.append("dict")
            ret.append([[self.wrap(k), self.wrap(v)] for k,v in o.items()])
            return [index]
        
        _0 = self._type_id(type(o))

        if hasattr(o, "__getnewargs__"):
            _1 = o.__getnewargs__()     # an iterable
            _1 = [self.wrap(i) for i in _1]
        else:
            _1 = None

        if o.__dict__ is None:
            _2 = None
        else:
            _2 = {}
            for k,v in o.__dict__.items():
                _2[k] = self.wrap(v)

        ret.append(_0)
        ret.append(_1)
        ret.append(_2)
        return [index]
    
    def run_pipe(self):
        o = self.wrap(self.obj)
        return [o, self.memo]



class _Unpickler:
    def __init__(self, obj, memo: list) -> None:
        self.obj = obj
        self.memo = memo
        self._unwrapped = [None] * len(memo)

    def tag(self, index, o):
        assert self._unwrapped[index] is None
        self._unwrapped[index] = o

    def unwrap(self, o, index=None):
        if type(o) in _BASIC_TYPES:
            return o
        assert type(o) is list

        if o[0] == "type":
            return _find_class(o[1])

        # reference
        if type(o[0]) is int:
            assert index is None    # index should be None
            index = o[0]
            if self._unwrapped[index] is None:
                o = self.memo[index]
                assert type(o) is list
                assert type(o[0]) is str
                self.unwrap(o, index)
                assert self._unwrapped[index] is not None
            return self._unwrapped[index]
        
        # concrete reference type
        if o[0] == "tuple":
            ret = tuple([self.unwrap(i) for i in o[1]])
            self.tag(index, ret)
            return ret
        if o[0] == "bytes":
            ret = bytes(o[1])
            self.tag(index, ret)
            return ret

        if o[0] == "list":
            ret = []
            self.tag(index, ret)
            for i in o[1]:
                ret.append(self.unwrap(i))
            return ret
        if o[0] == "dict":
            ret = {}
            self.tag(index, ret)
            for k,v in o[1]:
                ret[self.unwrap(k)] = self.unwrap(v)
            return ret
        
        # generic object
        cls, newargs, state = o
        cls = _find_class(o[0])
        # create uninitialized instance
        new_f = _find__new__(cls)
        if newargs is not None:
            newargs = [self.unwrap(i) for i in newargs]
            inst = new_f(cls, *newargs)
        else:
            inst = new_f(cls)
        self.tag(index, inst)
        # restore state
        if state is not None:
            for k,v in state.items():
                setattr(inst, k, self.unwrap(v))
        return inst

    def run_pipe(self):
        return self.unwrap(self.obj)


def _wrap(o):
    return _Pickler(o).run_pipe()

def _unwrap(packed: list):
    return _Unpickler(*packed).run_pipe()

def dumps(o) -> bytes:
    o = _wrap(o)
    return json.dumps(o).encode()

def loads(b) -> object:
    assert type(b) is bytes
    o = json.loads(b.decode())
    return _unwrap(o)