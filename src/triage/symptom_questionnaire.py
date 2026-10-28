"""Questionnaire data structures and loading helpers for cardiovascular screening."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping
from zipfile import ZipFile
from xml.etree import ElementTree


@dataclass(frozen=True)
class Option:
    """A selectable questionnaire answer."""

    value: str
    label: str | None = None

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("An option value cannot be empty.")


@dataclass(frozen=True)
class Question:
    """A single questionnaire question."""

    question_id: str
    text: str
    answer_type: str = "Single choice"
    options: tuple[Option, ...] = ()
    required: bool = True
    help_text: str = ""


@dataclass(frozen=True)
class SymptomDictionary:
    """Questionnaire definition, keyed by question identifier."""

    questions: Mapping[str, Question]

    def __post_init__(self) -> None:
        if not self.questions:
            raise ValueError("The symptom dictionary must contain questions.")

    def get(self, question_id: str) -> Question | None:
        return self.questions.get(question_id)


@dataclass
class UserAnswers:
    """Validated-enough answer container used by the triage pipeline.

    Validation is intentionally permissive for forward compatibility: unknown
    fields are retained, while rule evaluation safely ignores missing values.
    """

    answers: dict[str, Any] = field(default_factory=dict)

    def __init__(self, answers: Mapping[str, Any] | None = None, **kwargs: Any) -> None:
        self.answers = dict(answers or {})
        self.answers.update(kwargs)

    def get(self, question_id: str, default: Any = None) -> Any:
        return self.answers.get(question_id, default)

    def __getitem__(self, question_id: str) -> Any:
        return self.answers[question_id]

    def __setitem__(self, question_id: str, value: Any) -> None:
        self.answers[question_id] = value

    def to_dict(self) -> dict[str, Any]:
        return dict(self.answers)


_DEFAULT_QUESTIONS: tuple[Question, ...] = (
    Question("Q01", "Do you have chest pain, pressure, tightness or heaviness that is not easing with rest?", options=tuple(Option(v) for v in ("Yes", "No", "Not sure"))),
    Question("Q02", "Do you have a cold sweat, nausea, vomiting, or feel faint?", options=tuple(Option(v) for v in ("Yes", "No", "Not sure"))),
    Question("Q03", "Are you unable to speak a full sentence from breathlessness, or are your lips or fingertips blue or grey?", options=tuple(Option(v) for v in ("Yes", "No", "Not sure"))),
    Question("Q04", "Have you fainted today or feel you are about to?", options=tuple(Option(v) for v in ("Yes", "No", "Not sure"))),
    Question("Q05", "Do you have sudden one-sided weakness, facial drooping, or trouble speaking or seeing?", options=tuple(Option(v) for v in ("Yes", "No", "Not sure"))),
    Question("Q06", "Is chest discomfort spreading to an arm, shoulder, neck, jaw, or back?", options=tuple(Option(v) for v in ("Yes, now or in the last hour", "Yes, but it was earlier and has gone", "No", "I have no chest discomfort"))),
    Question("Q07", "What best describes chest discomfort in the last four weeks?", options=tuple(Option(v) for v in ("No chest discomfort", "Pressure, squeezing, tightness or heaviness", "Sharp or stabbing pain lasting only seconds", "Burning feeling, often after eating or when lying down", "Pain that changes when I press on my chest, move, or breathe in", "Not sure / something else"))),
    Question("Q12", "Do you feel short of breath while sitting or resting quietly?", options=tuple(Option(v) for v in ("No", "Mild, only sometimes", "Yes, often or getting worse"))),
    Question("Q13", "What activity makes you short of breath?", options=tuple(Option(v) for v in ("None, I breathe normally with everyday activity", "Only fast walking, hills or heavy work", "Walking on flat ground or climbing one flight of stairs", "Very light activity (a few steps, dressing, bathing)"))),
    Question("Q14", "How is your breathing when you lie flat to sleep?", options=tuple(Option(v) for v in ("No problem", "I need extra pillows to sleep comfortably", "I wake up at night gasping or breathless", "I cannot lie flat at all"))),
    Question("Q15", "Do you feel your heart racing, pounding, skipping beats or fluttering?", options=tuple(Option(v) for v in ("Never", "Occasional brief flutter (a few seconds)", "Frequent, or lasts several minutes", "Happening right now and feels very fast or irregular"))),
    Question("Q16", "Do you feel dizzy or light-headed?", options=tuple(Option(v) for v in ("Never", "Occasionally when I stand up quickly", "Often, or when exercising, or together with a racing heart", "I fainted in the last 4 weeks (not today)"))),
    Question("Q17", "Have you felt unusually tired?", options=tuple(Option(v) for v in ("No", "Mild, explained by busy life or poor sleep", "Unusual tiredness for more than 2 weeks", "Severe tiredness that limits daily tasks"))),
    Question("Q18", "Do you have swelling in your feet, ankles or legs?", options=tuple(Option(v) for v in ("No swelling", "Mild swelling of both ankles by evening that goes away overnight", "Both legs swollen most of the day, or swelling is increasing", "Only ONE leg is swollen, painful or red"))),
    Question("Q19", "What is your age in years?", answer_type="Number (18-120)"),
    Question("Q20", "What was your sex at birth?", options=tuple(Option(v) for v in ("Male", "Female", "Prefer not to say"))),
    Question("Q21", "Do you smoke or use tobacco?", options=tuple(Option(v) for v in ("Never", "Quit more than 1 year ago", "Quit within the last year", "Yes, currently"))),
    Question("Q22", "How often do you drink alcohol?", options=tuple(Option(v) for v in ("Never", "Occasionally (less than once a week)", "1 to 4 days a week", "Almost every day"))),
    Question("Q23", "Did a close relative have heart disease at an unusually young age?", options=tuple(Option(v) for v in ("Yes", "No", "I don't know"))),
    Question("Q24", "Has a doctor told you that you have any listed health conditions?", answer_type="Multiple choice"),
    Question("Q25", "What are your height (cm) and weight (kg)?", answer_type="Two numbers"),
)


def _fallback_dictionary() -> SymptomDictionary:
    return SymptomDictionary({question.question_id: question for question in _DEFAULT_QUESTIONS})


def _workbook_rows(path: Path) -> Iterable[list[str]]:
    """Read string cells from an xlsx file using only the standard library."""
    namespace = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    relationship_id = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/id"
    with ZipFile(path) as workbook:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in workbook.namelist():
            root = ElementTree.fromstring(workbook.read("xl/sharedStrings.xml"))
            shared = ["".join(t.text or "" for t in item.iter("{%s}t" % namespace["m"])) for item in root.findall("m:si", namespace)]
        book = ElementTree.fromstring(workbook.read("xl/workbook.xml"))
        relationships = ElementTree.fromstring(workbook.read("xl/_rels/workbook.xml.rels"))
        targets = {item.attrib["Id"]: item.attrib["Target"].lstrip("/") for item in relationships}
        for sheet in book.findall("m:sheets/m:sheet", namespace):
            target = targets[sheet.attrib[relationship_id]]
            if target not in workbook.namelist():
                target = "xl/" + target
            worksheet = ElementTree.fromstring(workbook.read(target))
            for row in worksheet.findall(".//m:sheetData/m:row", namespace):
                values: list[str] = []
                for cell in row.findall("m:c", namespace):
                    value = cell.find("m:v", namespace)
                    text = "" if value is None else value.text or ""
                    if cell.attrib.get("t") == "s" and text:
                        text = shared[int(text)]
                    elif cell.attrib.get("t") == "inlineStr":
                        text = "".join(t.text or "" for t in cell.iter("{%s}t" % namespace["m"]))
                    values.append(text)
                yield values


def load_questionnaire(path: str | Path | None = None) -> SymptomDictionary:
    """Load the questionnaire workbook, falling back to the bundled structure."""
    workbook_path = Path(path) if path else Path(__file__).parents[2] / "docs" / "04_symptom_questionnaire.xlsx"
    try:
        rows = iter(_workbook_rows(workbook_path))
        header = next(rows)
        indexes = {name: index for index, name in enumerate(header)}
        required = {"Q_ID", "Question (plain language)", "Answer type", "Answer options (separated by |)"}
        if not required.issubset(indexes):
            return _fallback_dictionary()
        questions: dict[str, Question] = {}
        for row in rows:
            if not row or not row[indexes["Q_ID"]].startswith("Q"):
                continue
            get = lambda key: row[indexes[key]] if indexes[key] < len(row) else ""
            options = tuple(Option(value.strip()) for value in get("Answer options (separated by |)").split("|") if value.strip() and value.strip() != "Number")
            questions[row[indexes["Q_ID"]].strip()] = Question(
                row[indexes["Q_ID"]].strip(), get("Question (plain language)"), get("Answer type"),
                options, get("Required").lower() == "yes" if "Required" in indexes else True,
                get("Help text shown to user") if "Help text shown to user" in indexes else "",
            )
        return SymptomDictionary(questions) if questions else _fallback_dictionary()
    except (OSError, KeyError, ValueError, IndexError, ElementTree.ParseError, TypeError):
        return _fallback_dictionary()


DEFAULT_QUESTIONNAIRE = _fallback_dictionary()

