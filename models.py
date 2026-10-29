COMPETENCIES = (
    ("skill_programming", "Programming"),
    ("skill_data_stats", "Data / stats"),
    ("skill_frontend_design", "Frontend design"),
    ("skill_business_pitch", "Business pitch"),
)


class CompetencyAverages:
    def __init__(self, averages):
        self.averages = averages

    @classmethod
    def from_students(cls, students):
        if not students:
            averages = [
                {"key": key, "label": label, "average": None}
                for key, label in COMPETENCIES
            ]
            return cls(averages)

        averages = []
        for key, label in COMPETENCIES:
            scores = [int(student[key]) for student in students]
            average = round(sum(scores) / len(scores), 2)
            averages.append({"key": key, "label": label, "average": average})
        return cls(averages)

    def to_dict(self):
        return {"competencies": self.averages}
