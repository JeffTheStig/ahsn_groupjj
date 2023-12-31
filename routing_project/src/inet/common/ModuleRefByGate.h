//
// Copyright (C) 2020 OpenSim Ltd.
//
// SPDX-License-Identifier: LGPL-3.0-or-later
//


#ifndef __INET_MODULEREFBYGATE_H
#define __INET_MODULEREFBYGATE_H

#include "inet/common/ModuleAccess.h"

namespace inet {

/**
 * This template class implements a module reference that is parameterized by
 * a gate of the referencing module. The reference can be set by providing the
 * gate of the referencing module. After the reference is set, it can be used
 * similarly to simple a C++ pointer. The pointer is automatically set to nullptr
 * when the referenced module is deleted.
 *
 * TODO follow connection
 */
template<typename T>
class INET_API ModuleRefByGate
{
  private:
    opp_component_ptr<T> referencedModule;
    cGate *gate = nullptr;

    void checkReference() const {
        if (referencedModule.getNullable() == nullptr) {
            if (gate == nullptr)
                throw cRuntimeError("Dereferencing uninitialized reference of type '%s'", opp_typename(typeid(T)));
            else
                throw cRuntimeError("Dereferencing nullptr of type '%s' referenced by '(%s)%s' through gate '%s'",
                                    opp_typename(typeid(T)), gate->getOwnerModule()->getClassName(), gate->getOwnerModule()->getFullPath().c_str(), gate->getFullName());
        }
    }

  public:
    T& operator*() const {
        checkReference();
        return *referencedModule;
    }

    T *operator->() const {
        checkReference();
        return referencedModule;
    }

    operator T *() const {
        return referencedModule;
    }

    explicit operator bool() const { return (bool)referencedModule; }

    T *getNullable() { return referencedModule.getNullable(); }
    const T *getNullable() const { return referencedModule.getNullable(); }

    T *get() { checkReference(); return referencedModule; }
    const T *get() const { checkReference(); return referencedModule; }

    cGate *getGate() { return gate; }
    const cGate *getGate() const { return gate; }

    void reference(cGate *gate, bool mandatory) {
        if (gate == nullptr)
            throw cRuntimeError("Gate is nullptr");
        if (this->gate != nullptr)
            throw cRuntimeError("Reference is already initialized");
        this->gate = gate;
        referencedModule = mandatory ? getConnectedModule<T>(gate) : findConnectedModule<T>(gate);
    }
};

} // namespace inet

#endif

