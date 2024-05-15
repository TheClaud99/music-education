/** @odoo-module **/

import {CalendarModel} from "@web/views/calendar/calendar_model";
import session from "web.session";

export class TeacherCalendarModel extends CalendarModel {
    /**
     * Override of method loadFilterSection in web/static/src/views/calendar/calendar_model.js
     * @override
     * @protected
     */
    async loadFilterSection(fieldName, filterInfo, previousSection) {
        const previousFilters = previousSection ? previousSection.filters : [];
        const is_teacher = await session.user_has_group("education.education_teacher");
        if (previousFilters.length !== 0 || is_teacher) {
            return super.loadFilterSection(fieldName, filterInfo, previousSection);
        }
        const ret = await super.loadFilterSection(
            fieldName,
            filterInfo,
            previousSection
        );
        const filters = ret.filters;
        const previousActiveFilter = filters.find((f) => f.active);
        const allFilter = filters.find((f) => f.type === "all");

        previousActiveFilter.active = false;
        allFilter.active = true;

        return ret;
    }
}
