/** @odoo-module **/

import { CalendarModel } from "@web/views/calendar/calendar_model";


export class TeacherCalendarModel extends CalendarModel {
    /**
     * @protected
     */
    async loadFilterSection(fieldName, filterInfo, previousSection) {
        const previousFilters = previousSection
            ? previousSection.filters
            : [];
        if (previousFilters.length != 0) {
            return super.loadFilterSection(fieldName, filterInfo, previousSection);
        }
        const ret = await super.loadFilterSection(fieldName, filterInfo, previousSection);
        const filters = ret.filters;
        const previousActiveFilter = filters.find((f) => f.active);
        const allFilter = filters.find((f) => f.type === "all");

        previousActiveFilter.active = false;
        allFilter.active = true;

        return ret;
    }
}

