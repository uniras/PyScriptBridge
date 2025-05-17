
class PysBridge {
    static #pysBridge = {};
    static #pysBridgeGlobalName = "$pys_bridge_global_name";

    #states
    #refs
    #funcs
    #promise

    constructor(pysid) {
        pysid = PysBridge.get_uuid_ref(pysid);
        this.#states = {};
        this.#refs = {};
        this.#funcs = {};
        this.#promise = this.#createPromise();
        PysBridge.#pysBridge[pysid] = this;
    }

    #createPromise() {
        let resolve;
        const promise = new Promise((res) => resolve = res);
        return { promise, resolve };
    }

    resolve() {
        this.#promise.resolve();
    }

    async wait() {
        await this.#promise.promise;
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

    ref(name) {
        if (typeof this.#refs[name] !== "undefined") {
            return this.#refs[name];
        } else {
            throw new Error(`Var ${name} not found.`);
        }
    }

    add_ref(name, value) {
        this.#refs[name] = value;
    }

    add_state(name, stateObject, stateSetterObject) {
        this.#states[name] = { getter: stateObject, setter: stateSetterObject };
    }

    add_func(name, funcObject) {
        this.#funcs[name] = funcObject;
    }

    async call_func(name, ...args) {
        await this.wait();
        if (typeof this.#funcs[name] === "function") {
            await this.#funcs[name](...args);
        } else {
            throw new Error(`Function ${name} not function.`);
        }
    }

    static get_uuid_ref(pysid) {
        if (typeof pysid !== "string") throw new Error("UUID must be a string.");
        if (pysid === "") pysid = PysBridge.#pysBridgeGlobalName;
        return pysid;
    }

    static create_pys_bridge(pysid) {
        pysid = PysBridge.get_uuid_ref(pysid);
        if (typeof PysBridge.#pysBridge[pysid] === "undefined") {
            return new PysBridge(pysid);
        }
    }

    static get_pys_bridge(pysid) {
        pysid = PysBridge.get_uuid_ref(pysid);
        if (typeof PysBridge.#pysBridge[pysid] !== "undefined") {
            return PysBridge.#pysBridge[pysid];
        } else {
            throw new Error(`Bridge id ${pysid} not found.`);
        }
    }
}

globalThis.PysBridge = PysBridge;
