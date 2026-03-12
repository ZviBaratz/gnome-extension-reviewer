import {SharedHelper} from './shared_helper.js';

export class ParentB {
    constructor() {
        this._helper = new SharedHelper();
        this._active = true;
    }

    disable() {
        this._active = false;
        // helper cleanup is handled by ParentA
    }
}
