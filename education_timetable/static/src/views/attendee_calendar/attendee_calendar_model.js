/** @odoo-module **/

import { AttendeeCalendarModel } from "@calendar/views/attendee_calendar/attendee_calendar_model";
import { patch } from "@web/core/utils/patch";

patch(
    AttendeeCalendarModel.prototype,
    "attendee_calendar_model_everybody_by_default_patch",
    {
        /**
         * @protected
         */
        async loadFilterSection(fieldName, filterInfo, previousSection) {
            const previousFilters = previousSection
                ? previousSection.filters
                : [];
            if (previousFilters.length != 0) {
                return this._super.apply(this, arguments);
            }
            const ret = await this._super.apply(this, arguments);
            const filters = ret.filters;
            const previousActiveFilter = filters.find((f) => f.active);
            const allFilter = filters.find((f) => f.type === "all");

            previousActiveFilter.active = false;
            allFilter.active = true;

            return ret;
        },
    }
);
