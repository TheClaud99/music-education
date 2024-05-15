/** @odoo-module **/

import {AttendeeCalendarCommonPopover} from "@calendar/views/attendee_calendar/common/attendee_calendar_common_popover";
import {patch} from "@web/core/utils/patch";

patch(
    AttendeeCalendarCommonPopover.prototype,
    "attendee_calendar_model_everybody_by_default_patch",
    {
        get isEventDeletable() {
            return this.props.model.canDelete;
        },
    }
);
