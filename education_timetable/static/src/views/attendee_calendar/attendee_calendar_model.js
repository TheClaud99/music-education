/** @odoo-module **/

import { AttendeeCalendarModel } from "@calendar/views/attendee_calendar/attendee_calendar_model";
import { patch } from "@web/core/utils/patch";

patch(
    AttendeeCalendarModel.prototype,
    {
        /**
         * @protected
         */
        async loadFilterSection(fieldName, filterInfo, previousSection) {
            const previousFilters = previousSection
                ? previousSection.filters
                : [];
            if (previousFilters.length != 0) {
                return super.loadFilterSection(...arguments);
            }
            const ret = await super.loadFilterSection(...arguments);
            const filters = ret.filters;
            const previousActiveFilter = filters.find((f) => f.active);
            const allFilter = filters.find((f) => f.type === "all");

            previousActiveFilter.active = false;
            allFilter.active = true;

            return ret;
        },
    }
);
