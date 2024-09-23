/** @odoo-module **/

import {TeacherCalendarModel} from "@education_timetable/views/teacher_calendar/teacher_calendar_model.esm";
import {TeacherCalendarRenderer} from "@education_timetable/views/teacher_calendar/teacher_calendar_renderer.esm";
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
