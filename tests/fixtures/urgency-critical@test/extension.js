import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class UrgencyCriticalExtension extends Extension {
    enable() {
        const source = new Main.MessageTray.Source('Test');
        const notification = new Main.MessageTray.Notification(source, 'Hello');
        // BAD: CRITICAL urgency for a non-system notification
        notification.urgency = Main.MessageTray.Urgency.CRITICAL;
        Main.messageTray.add(source);
        source.showNotification(notification);
    }

    disable() {}
}
