from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta


class DoctorScheduleWizard(models.TransientModel):
    _name = "doctor.schedule.wizard"
    _description = "Doctor Schedule Wizard"

    doctor_id = fields.Many2one(
        "hr_hospital.doctor",
        string="Doctor",
        required=True,
        domain=[("speciality_id", "!=", False)],
    )
    week_start = fields.Date(
        required=True,
        default=fields.Date.today,
    )
    weeks_count = fields.Integer(
        string="Number of Weeks",
        required=True,
        default=1,
    )
    schedule_type = fields.Selection([
        ("standard", "Standard"),
        ("even_week", "Even Week"),
        ("odd_week", "Odd Week"),
    ], default="standard")

    mon = fields.Boolean(string="Monday", default=True)
    tue = fields.Boolean(string="Tuesday", default=True)
    wed = fields.Boolean(string="Wednesday", default=True)
    thu = fields.Boolean(string="Thursday", default=True)
    fri = fields.Boolean(string="Friday", default=True)
    sat = fields.Boolean(string="Saturday", default=False)
    sun = fields.Boolean(string="Sunday", default=False)

    time_start = fields.Float(string="Start Time", default=9.0)
    time_end = fields.Float(string="End Time", default=18.0)
    break_start = fields.Float(string="Break From", default=13.0)
    break_end = fields.Float(string="Break To", default=14.0)

    @api.constrains("time_start", "time_end", "break_start", "break_end")
    def _check_times(self):
        for rec in self:
            if rec.time_end <= rec.time_start:
                raise ValidationError(
                    "End time must be greater than start time!"
                )
            if rec.break_start and rec.break_end:
                if rec.break_end <= rec.break_start:
                    raise ValidationError(
                        "Break end must be greater than break start!"
                    )
                if (
                    rec.break_start < rec.time_start
                    or rec.break_end > rec.time_end
                ):
                    raise ValidationError(
                        "Break time must be within working hours!"
                    )

    @api.constrains("weeks_count")
    def _check_weeks_count(self):
        for rec in self:
            if rec.weeks_count < 1 or rec.weeks_count > 52:
                raise ValidationError(
                    "Number of weeks must be between 1 and 52!"
                )

    def _get_working_days(self):
        self.ensure_one()
        days = []
        if self.mon:
            days.append(0)
        if self.tue:
            days.append(1)
        if self.wed:
            days.append(2)
        if self.thu:
            days.append(3)
        if self.fri:
            days.append(4)
        if self.sat:
            days.append(5)
        if self.sun:
            days.append(6)
        return days

    def action_generate_schedule(self):
        self.ensure_one()
        working_days = self._get_working_days()
        if not working_days:
            raise ValidationError(
                "Please select at least one working day!"
            )

        week_start = self.week_start
        monday = week_start - timedelta(days=week_start.weekday())

        created_count = 0
        for week in range(self.weeks_count):
            current_monday = monday + timedelta(weeks=week)
            week_number = current_monday.isocalendar()[1]

            if self.schedule_type == "even_week" and week_number % 2 != 0:
                continue
            if self.schedule_type == "odd_week" and week_number % 2 == 0:
                continue

            for day_offset in working_days:
                current_date = current_monday + timedelta(days=day_offset)

                existing = self.env["doctor.schedule"].search([
                    ("doctor_id", "=", self.doctor_id.id),
                    ("date", "=", current_date),
                ])
                if existing:
                    continue

                self.env["doctor.schedule"].create({
                    "doctor_id": self.doctor_id.id,
                    "date": current_date,
                    "time_start": self.time_start,
                    "time_end": self.time_end,
                    "schedule_type": "workday",
                    "notes": (
                        f"Break: {int(self.break_start):02d}:"
                        f"{int((self.break_start % 1)*60):02d}"
                        f" - {int(self.break_end):02d}:"
                        f"{int((self.break_end % 1)*60):02d}"
                    ),
                })
                created_count += 1

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Schedule Generated!",
                "message": (
                    f"Successfully created {created_count} schedule "
                    f"entries for {self.doctor_id.name}."
                ),
                "sticky": False,
                "type": "success",
            },
        }
