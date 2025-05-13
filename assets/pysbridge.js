globalThis.__pysPromises = {};
globalThis.__pysStates = {};
globalThis.__pysRefs = {};
globalThis.__pysFunctions = {};

/**
 * Create a new promise with a unique name.
 * Resolved promises cannot be reused.
 *
 * @param {*} promiseName - The name of the promise.
 */
globalThis.pys_promise = (promiseName) => {
    if (typeof globalThis.__pysPromises[promiseName] === "undefined") {
        let resolve;
        const promise = new Promise((res) => resolve = res);
        globalThis.__pysPromises[promiseName] = { promise, resolve };
    }
}

/**
 * Wait for a promise to be resolved.
 * If the promise is not defined, it will be created.
 * This function will block until the promise is resolved.
 *
 * @param {*} promiseName - The name of the promise.
 */
globalThis.pys_wait = async (promiseName) => {
    if (typeof globalThis.__pysPromises[promiseName] === "undefined") {
        globalThis.pys_promise(promiseName);
    }
    await globalThis.__pysPromises[promiseName].promise;
};

/**
 * Resolve a promise.
 * If the promise is not defined, it will be created and resolved.
 *
 * @param {*} promiseName - The name of the promise.
 */
globalThis.pys_resolve = (promiseName) => {
    if (typeof globalThis.__pysPromises[promiseName] === "undefined") {
        globalThis.pys_promise(promiseName);
    }
    globalThis.__pysPromises[promiseName].resolve();
}

/**
 * Register a new state.
 *
 * @param {*} stateName - The name of the state.
 * @param {*} stateObject - The object representing the state.
 * @param {*} stateSetterObject - The function to update the state.
 */
globalThis.pys_register_state = (stateName, stateObject, stateSetterObject) => {
    globalThis.__pysStates[stateName] = {getter: stateObject, setter: stateSetterObject};
}

/**
 * Register a new reference.
 *
 * @param {*} refName - The name of the reference.
 * @param {*} refObject - The object representing the reference.
 */
globalThis.pys_register_ref = (refName, refObject) => {
    globalThis.__pysRefs[refName] = refObject;
}

/**
 * Register a new function.
 *
 * @param {*} functionName - The name of the function.
 * @param {*} functionObject - The object representing the function.
 */
globalThis.pys_func = (functionName, functionObject) => {
    globalThis.__pysFunctions[functionName] = functionObject;
}

/**
 * Get the value of a state.
 *
 * @param {*} stateName - The name of the state.
 * @returns {*} - The value of the state.
 */
globalThis.pys_get = (stateName) => {
    if (typeof globalThis.__pysStates[stateName] !== "undefined") {
        return globalThis.__pysStates[stateName].getter;
    } else {
        throw new Error(`State ${stateName} not found.`);
    }
}

/**
 * Set the value of a state.
 *
 * @param {*} stateName - The name of the state.
 * @param {*} value - The value to set.
 */
globalThis.pys_set = (stateName, value) => {
    if (typeof globalThis.__pysStates[stateName] !== "undefined") {
        globalThis.__pysStates[stateName].setter(value);
    } else {
        throw new Error(`State ${stateName} not found.`);
    }
}

/**
 * Get the value of a reference.
 *
 * @param {*} refName - The name of the reference.
 * @returns {*} - The value of the reference.
 */
globalThis.pys_ref = (refName) => {
    if (typeof globalThis.__pysRefs[refName] !== "undefined") {
        return globalThis.__pysRefs[refName];
    } else {
        throw new Error(`Ref ${refName} not found.`);
    }
}

/**
 * Call a function.
 * This function will wait for the promise to be resolved before calling the function.
 *
 * @param {*} functionName - The name of the function.
 * @param {*} promiseName - The name of the promise. if it is not string, no wait.
 * @param {...*} args - The arguments to pass to the function.
 */
globalThis.pys_call_func = async (functionName, promiseName, ...args) => {
    if (typeof promiseName === "string" && promiseName !== "") {
        await globalThis.pys_wait(promiseName);
    }
    if (typeof globalThis.__pysFunctions[functionName] === "function") {
        await globalThis.__pysFunctions[functionName](...args);
    } else {
        throw new Error(`Function ${functionName} not function.`);
    }
}
