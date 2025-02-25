#include "pocketpy/gc.h"

namespace pkpy{

    int ManagedHeap::sweep(){
        std::vector<PyObject*> alive;
        for(PyObject* obj: gen){
            if(obj->gc.marked){
                obj->gc.marked = false;
                alive.push_back(obj);
            }else{
#if PK_DEBUG_GC_STATS
                deleted[obj->type] += 1;
#endif
                if(_gc_on_delete) _gc_on_delete(vm, obj);
                obj->~PyObject();
                pool64_dealloc(obj);
            }
        }

        // clear _no_gc marked flag
        for(PyObject* obj: _no_gc) obj->gc.marked = false;

        int freed = gen.size() - alive.size();
        // std::cout << "GC: " << alive.size() << "/" << gen.size() << " (" << freed << " freed)" << std::endl;
        gen.clear();
        gen.swap(alive);
        return freed;
    }

    void ManagedHeap::_auto_collect(){
#if !PK_DEBUG_NO_AUTO_GC
        if(_gc_lock_counter > 0) return;
        if(gc_counter < gc_threshold) return;
        gc_counter = 0;
        collect();
        gc_threshold = gen.size() * 2;
        if(gc_threshold < kMinGCThreshold) gc_threshold = kMinGCThreshold;
#endif
    }

    int ManagedHeap::collect(){
        if(_gc_lock_counter > 0) FATAL_ERROR();
        mark();
        int freed = sweep();
        return freed;
    }

    ManagedHeap::~ManagedHeap(){
        for(PyObject* obj: _no_gc) { obj->~PyObject(); pool64_dealloc(obj); }
        for(PyObject* obj: gen) { obj->~PyObject(); pool64_dealloc(obj); }
#if PK_DEBUG_GC_STATS
        for(auto& [type, count]: deleted){
            std::cout << "GC: " << obj_type_name(vm, type) << "=" << count << std::endl;
        }
#endif
    }


void FuncDecl::_gc_mark() const{
    code->_gc_mark();
    for(int i=0; i<kwargs.size(); i++) PK_OBJ_MARK(kwargs[i].value);
}

}   // namespace pkpy