// Copyright 2024 Test Author
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program. If not, see <http://www.gnu.org/licenses/>.

/*
 * Based on code from http://frippery.org/extensions/
 */

import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

// This URL should still fire R-SEC-03 (not a license URL)
const API_URL = 'http://example.com/api';

export default class LicenseHeaderExtension extends Extension {
    enable() {}
    disable() {}
}
