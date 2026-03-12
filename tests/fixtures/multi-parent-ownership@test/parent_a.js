import {SharedHelper} from './shared_helper.js';

export class ParentA {
    constructor() {
        this._helper = new SharedHelper();
    }

    disable() {
        this._helper.disconnect_all();
        this._helper = null;
    }
}
