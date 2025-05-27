
const PRIVATE_CONSTRUCTOR_KEY = Symbol()

class PysBridge {
    static #pysBridge = {};
    static #pysBridgeGlobalName = "$pys_bridge_global_name";

    #states
    #refs
    #funcs
    #promise = {}

    static #get_uuid_ref(pysid) {
        if (typeof pysid !== "string") throw new Error("UUID must be a string.");
        if (pysid === "") pysid = PysBridge.#pysBridgeGlobalName;
        return pysid;
    }

    static create_pys_bridge(pysid) {
        pysid = PysBridge.#get_uuid_ref(pysid);
        if (typeof PysBridge.#pysBridge[pysid] === "undefined") {
            return new PysBridge(pysid, PRIVATE_CONSTRUCTOR_KEY);
        } else {
            return PysBridge.#pysBridge[pysid];
        }
    }

    static get_pys_bridge(pysid) {
        pysid = PysBridge.#get_uuid_ref(pysid);
        if (typeof PysBridge.#pysBridge[pysid] !== "undefined") {
            return PysBridge.#pysBridge[pysid];
        } else {
            throw new Error(`Bridge id ${pysid} not found.`);
        }
    }

    static has_pys_bridge(pysid) {
        pysid = PysBridge.#get_uuid_ref(pysid);
        return typeof PysBridge.#pysBridge[pysid] !== "undefined";
    }

    constructor(pysid, privateConstructorKey) {
        if (privateConstructorKey !== PRIVATE_CONSTRUCTOR_KEY) {
            throw new Error("Cannot instantiate PysBridge directly.");
        }
        pysid = PysBridge.#get_uuid_ref(pysid);
        this.#states = {};
        this.#refs = {};
        this.#funcs = {};
        PysBridge.#pysBridge[pysid] = this;
    }

    #createPromise() {
        let resolve;
        const promise = new Promise((res) => resolve = res);
        return { promise, resolve };
    }

    #resolve(funcname) {
        if (typeof this.#promise[funcname] === "undefined") {
            this.#promise[funcname] = this.#createPromise();
        }
        this.#promise[funcname].resolve();
    }

    async #wait(funcname) {
        if (typeof this.#promise[funcname] === "undefined") {
            this.#promise[funcname] = this.#createPromise();
        }
        await this.#promise[funcname].promise;
    }

    add_state(name, stateObject, stateSetterObject) {
        this.#states[name] = { getter: stateObject, setter: stateSetterObject };
    }

    state(name) {
        if (typeof this.#states[name] !== "undefined") {
            return this.#states[name].getter;
        } else {
            throw new Error(`State ${name} not found.`);
        }
    }

    set_state(name, value) {
        if (typeof this.#states[name] !== "undefined") {
            this.#states[name].setter(value);
        } else {
            throw new Error(`State ${name} not found.`);
        }
    }

    has_state(name) {
        return typeof this.#states[name] !== "undefined";
    }

    add_ref(name, value) {
        this.#refs[name] = value;
    }

    ref(name) {
        if (typeof this.#refs[name] !== "undefined") {
            return this.#refs[name];
        } else {
            throw new Error(`Var ${name} not found.`);
        }
    }

    has_ref(name) {
        return typeof this.#refs[name] !== "undefined";
    }

    add_func(name, funcObject) {
        if (typeof funcObject !== "function") {
            throw new Error("Function must be a function.");
        }
        this.#funcs[name] = funcObject;
        this.#resolve(name);
    }

    async call_func(name, ...args) {
        await this.#wait(name);
        if (typeof this.#funcs[name] === "function") {
            await this.#funcs[name](...args);
        }
    }

    has_func(name) {
        return typeof this.#funcs[name] === "function";
    }
}

globalThis.PysBridge = PysBridge;
