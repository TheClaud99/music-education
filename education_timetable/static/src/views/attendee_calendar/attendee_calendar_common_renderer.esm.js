/** @odoo-module **/

import {AttendeeCalendarCommonRenderer} from "@calendar/views/attendee_calendar/common/attendee_calendar_common_renderer";
import {patch} from "@web/core/utils/patch";

// patch(
//     AttendeeCalendarCommonRenderer.prototype,
//     "attendee_calendar_common_renderer_lesson_patch",
//     {
//         /**
//          * @protected
//          */
//         onEventRender(info) {
//             this._super(...arguments);
//             const { el, event } = info;
//             const record = this.props.model.records[event.id];

//             if (record) {
//                 record.title = "boh";
//                 switch (record.rawRecord.payment_state) {
//                     case "paid":
//                         record.dotClass = "text-success";
//                         break;
//                     case "not_paid":
//                         record.dotClass = "text-danger";
//                         break;
//                     case "partial":
//                         record.dotClass = "text-warning";
//                         break;
//                     default:
//                         record.dotClass = "d-none";
//                 }
//             }
//         },
//     }
// );
