/** @odoo-module **/

import {CalendarCommonPopover} from "@web/views/calendar/calendar_common/calendar_common_popover";

export class TeacherCalendarCommonPopover extends CalendarCommonPopover {
    get isCurrentUserAttendee() {
        return this.props.record.rawRecord.partner_ids.includes(this.user.partnerId);
    }

    get isCurrentUserOrganizer() {
        return this.props.record.rawRecord.partner_id[0] === this.user.partnerId;
    }

    get isEventPrivate() {
        return this.props.record.rawRecord.privacy === "private";
    }

    get displayAttendeeAnswerChoice() {
        return (
            this.props.record.rawRecord.partner_ids.some(
                (partner) => partner !== this.user.partnerId
            ) && this.props.record.isCurrentPartner
        );
    }

    get isEventDetailsVisible() {
        return true;
    }

    get isEventArchivable() {
        return false;
    }

    /**
     * @override
     */
    get isEventDeletable() {
        return (
            super.isEventDeletable &&
            this.isCurrentUserAttendee &&
            !this.isEventArchivable
        );
    }

    /**
     * @override
     */
    get isEventEditable() {
        return false;
    }

    async onClickArchive() {
        await this.props.model.archiveRecord(this.props.record);
    }
}
