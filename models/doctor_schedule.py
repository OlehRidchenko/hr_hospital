from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DoctorSchedule(models.Model):
    _name = "doctor.schedule"
    _description = "Doctor Schedule"

    doctor_id = fields.Many2one(
        "hr_hospital.doctor",
        string="Doctor",
        required=True,
        ondelete="cascade",
        domain=[("speciality_id", "!=", False)],
    )
    day_of_week = fields.Selection([
        ("mon", "Monday"),
        ("tue", "Tuesday"),
        ("wed", "Wednesday"),
        ("thu", "Thursday"),
        ("fri", "Friday"),
        ("sat", "Saturday"),
        ("sun", "Sunday"),
    ], string="Day of Week")

    date = fields.Date(string="Specific Date")

    time_start = fields.Float(string="Start Time")
    time_end = fields.Float(string="End Time")

    duration = fields.Float(
        string="Duration (hours)",
        compute="_compute_duration",
        store=True,
    )

    schedule_type = fields.Selection([
        ("workday", "Work Day"),
        ("vacation", "Vacation"),
        ("sick_leave", "Sick Leave"),
        ("conference", "Conference"),
    ], string="Type")

    notes = fields.Char()

    _sql_constraints = [
        (
            "time_end_after_start",
            "CHECK(time_end > time_start)",
            "End time must be greater than start time!",
        ),
    ]

    @api.depends("time_start", "time_end")
    def _compute_duration(self):
        for rec in self:
            rec.duration = rec.time_end - rec.time_start

    @api.constrains("time_start", "time_end")
    def _check_time(self):
        for rec in self:
            if rec.time_end and rec.time_start:
                if rec.time_end <= rec.time_start:
                    raise ValidationError(
                        "End time must be greater than start time!"
                    )
                if rec.time_start < 0 or rec.time_end > 24:
                    raise ValidationError(
                        "Time must be between 0 and 24 hours!"
                    )

    @api.constrains("date", "day_of_week")
    def _check_date_or_day(self):
        for rec in self:
            if not rec.date and not rec.day_of_week:
                raise ValidationError(
                    "Please specify either a specific date "
                    "or a day of the week!"
                )

    @api.constrains("doctor_id", "date")
    def _check_duplicate_schedule(self):
        for rec in self:
            if not rec.date:
                continue
            duplicate = self.search([
                ("id", "!=", rec.id),
                ("doctor_id", "=", rec.doctor_id.id),
                ("date", "=", rec.date),
                ("schedule_type", "=", rec.schedule_type),
            ])
            if duplicate:
                raise ValidationError(
                    f"Doctor '{rec.doctor_id.name}' already has a "
                    f"'{rec.schedule_type}' schedule on {rec.date}!"
                )

    def name_get(self):
        result = []
        for rec in self:
            date_str = str(rec.date) if rec.date else rec.day_of_week or ""
            time_str = (
                f"{int(rec.time_start):02d}:"
                f"{int((rec.time_start % 1) * 60):02d}"
                f" - "
                f"{int(rec.time_end):02d}:"
                f"{int((rec.time_end % 1) * 60):02d}"
            )
            name = f"{rec.doctor_id.name} | {date_str} | {time_str}"
            result.append((rec.id, name))
        return result
