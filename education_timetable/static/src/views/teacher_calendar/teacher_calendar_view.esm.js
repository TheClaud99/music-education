/** @odoo-module **/

import {TeacherCalendarModel} from "@education_timetable/views/teacher_calendar/teacher_calendar_model";
import {TeacherCalendarRenderer} from "@education_timetable/views/teacher_calendar/teacher_calendar_renderer";
import {calendarView} from "@web/views/calendar/calendar_view";
// Import { AttendeeCalendarController } from "@calendar/views/attendee_calendar/attendee_calendar_controller";
import {registry} from "@web/core/registry";

export const teacherCalendarView = {
    ...calendarView,
    // Controller: AttendeeCalendarController,
    Model: TeacherCalendarModel,
    Renderer: TeacherCalendarRenderer,
    // ButtonTemplate: "calendar.AttendeeCalendarController.controlButtons",
};

registry.category("views").add("teacher_calendar", teacherCalendarView);
