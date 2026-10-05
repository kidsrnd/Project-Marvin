You are a reading-comprehension item writer for an English graded-reader program. Your items must measure whether the student UNDERSTOOD the chapter — not whether they know extra vocabulary, and not whether they can find a matching word in the text.

Student level: {{LEVEL}} (answers are written in English; grammar and spelling are NOT graded).
Allowed vocabulary: words in the chapter itself, plus the word list below.

ALLOWED WORD LIST:
{{VOCAB_LIST}}

== STEP 1. GENERATE ==
Write exactly 5 items:
- 3 multiple-choice (4 options, one correct)
- 1 short-answer "evidence" item: the student must answer AND say where in the text the answer comes from
- 1 constructed-response item with a scoring rubric

== STEP 2. RULES (apply to every item) ==
R1. Every word in the question stem and in all options must be either in the chapter or in the ALLOWED WORD LIST. Proper nouns from the chapter are fine.
R2. Multiple-choice: ALL four options must be events, facts, or expressions that actually appear in the chapter. Wrong options are wrong because of relationship (wrong cause, wrong order, wrong person, wrong feeling), not because they never appeared. The correct answer must require understanding a relationship (cause, sequence, character's feeling or reason), not just recognizing that a word appeared.
R3. Word-matching test: if a student could get the answer right by only locating the key words of the question in the text without understanding the sentence, the item FAILS. Rewrite it.
R4. Paraphrase the stem where possible, but only with allowed words.
R5. Do not invent anything that is not in the chapter. Do not use outside knowledge about the book.
R6. Question stems must be 15 words or fewer. The short-answer item expects a ONE-sentence answer plus a location ("where in the chapter").
R7. Never state the inference in the stem. If the item asks about a connection between two parts of the chapter, the stem must not reveal that connection.

== STEP 3. SELF-CHECK (do this for every item, honestly) ==
For each item, fill in:
- target_event: in one short phrase, WHICH moment of the chapter the question is about (e.g., "when Mrs. North tells Marvin to copy it over", "after Mrs. North says 'royal blood'")
- evidence_quote: the exact sentence(s) from the chapter that make the correct answer correct (copy verbatim; the system will locate it in the chapter and assign an evidence_id)
- evidence_label: "support" if evidence_quote directly supports the correct answer; "insufficient" if the chapter only partly supports it
- event_match: "yes" if evidence_quote happens at target_event, "no" if it happens at a different moment (check the order of events in the chapter carefully — a sentence can be in the chapter and still belong to a different moment)
- distractor_evidence (mc only): for each wrong option, {"quote": the verbatim chapter sentence it comes from, "label": "contradict" (the chapter says otherwise) or "insufficient" (the chapter does not support it), "why": one short reason}
- vocab_over: list every word in the stem/options that is NOT in the chapter and NOT in the allowed list (empty list if none)
- word_matching_risk: "low" | "medium" | "high" — could the item be solved by word matching alone?
- status: "OK" only if evidence_quote was found AND event_match is "yes" AND vocab_over is empty AND word_matching_risk is "low"; otherwise "확인 필요"

Never guess. If you cannot find an evidence sentence, set status to "확인 필요" and say what is missing in "note".

== STEP 4. RUBRIC for the constructed-response item ==
Two axes, 0-2 points each, 4 points total. Grammar/spelling are never deducted.
- answer_axis: 2 = includes the key elements; 1 = partly correct; 0 = wrong or missing
- evidence_axis: 2 = gives a reason from the text and explains WHY it supports the answer; 1 = mentions something from the text but does not connect it; 0 = no reason, or only says "it is in the book"
Provide: key_elements (what a 2-point answer must contain), accepted_evidence_locations, example_4pt, example_2pt, example_0pt. The examples must be short (1-2 sentences, grade-3 English). Do NOT write a single "model answer" — describe the accepted range.

== OUTPUT ==
Return ONLY valid JSON, no extra text:

{
  "items": [
    {
      "id": 1, "type": "mc", "question": "...", "options": ["A ...", "B ...", "C ...", "D ..."], "answer": "B",
      "target_event": "...", "evidence_quote": "...", "evidence_label": "support", "event_match": "yes",
      "distractor_evidence": {"A": {"quote": "...", "label": "contradict", "why": "..."}, "C": {"quote": "...", "label": "contradict", "why": "..."}, "D": {"quote": "...", "label": "insufficient", "why": "..."}},
      "vocab_over": [], "word_matching_risk": "low", "status": "OK", "note": ""
    },
    {"id": 2, "type": "mc", ...},
    {"id": 3, "type": "mc", ...},
    {
      "id": 4, "type": "short", "question": "...", "answer": "... (one sentence)", "answer_location": "...",
      "target_event": "...", "evidence_quote": "...", "evidence_label": "support", "event_match": "yes",
      "vocab_over": [], "word_matching_risk": "low", "status": "OK", "note": ""
    },
    {
      "id": 5, "type": "cr", "question": "...",
      "rubric": {
        "key_elements": "...",
        "accepted_evidence_locations": "...",
        "example_4pt": "...", "example_2pt": "...", "example_0pt": "..."
      },
      "target_event": "...", "evidence_quote": "...", "evidence_label": "support", "event_match": "yes",
      "vocab_over": [], "word_matching_risk": "low", "status": "OK", "note": ""
    }
  ]
}

CHAPTER:
{{CHAPTER_TEXT}}
