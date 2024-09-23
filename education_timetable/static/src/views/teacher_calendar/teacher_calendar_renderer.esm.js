/** @odoo-module **/

import {ActionSwiper} from "@web/core/action_swiper/action_swiper";
import {CalendarCommonRenderer} from "@web/views/calendar/calendar_common/calendar_common_renderer";
import {CalendarRenderer} from "@web/views/calendar/calendar_renderer";
import {CalendarYearRenderer} from "@web/views/calendar/calendar_year/calendar_year_renderer";
import {TeacherCalendarCommonPopover} from "@education_timetable/views/teacher_calendar/teacher_calendar_common_popover.esm";

export class TeacherCommonCalendarRenderer extends CalendarCommonRenderer {
    setup() {
        super.setup();
    }

    get options() {
        const options = super.options;
        options.droppable = false;
        options.editable = false;
        options.eventDragStart = false;
        return options;
    }
}

TeacherCommonCalendarRenderer.components = {
    ...CalendarCommonRenderer.components,
    Popover: TeacherCalendarCommonPopover,
};

export class TeacherCalendarRenderer extends CalendarRenderer {}
TeacherCalendarRenderer.components = {
    // ...CalendarRenderer.components,
    day: TeacherCommonCalendarRenderer,
    week: TeacherCommonCalendarRenderer,
    month: TeacherCommonCalendarRenderer,
    year: CalendarYearRenderer,
    ActionSwiper,
};
