# FUNCTIONALITY.md.

### Functionality A: Chatbot FAQ Support
- Input:
  - Free-text user question (for example: "When are meetings?")
- Output:
  - Natural-language answer shown to the user
- Success:
  - Returns an answer relevant to the user question
- Failure/Edge Cases:
  - Unknown question -> return fallback like "I don't have that information yet."
  - Empty input -> prompt user to enter a question

### Functionality B: Member Registration
- Input:
  - Free-text or form submission with member fields (for example: name, email, major, year)
- Output:
  - Submission result message (`success`, `exists`, or `incomplete`)
- Success:
  - Required fields are present and record is saved to the database
- Failure/Edge Cases:
  - Missing required field(s) -> return `incomplete` with missing field list
  - Duplicate email -> return `exists`
  - Invalid formats -> return validation error

