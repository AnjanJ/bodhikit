---
description: "Assessment framework: question templates by Bloom's level, exercise templates, mastery criteria, adaptive questioning strategy"
user-invocable: false
---

# Assessment Framework

This knowledge base defines how BodhiKit assesses learner skill levels, designs exercises, and measures mastery. Referenced by the `skill-assessor` agent and assessment-related skills.

---

## Adaptive Questioning Strategy

### Entry Point

Always start assessment at **Bloom's Level 3 (Apply)**. This is the pivot point:
- If they succeed at Level 3, escalate to Level 4, then Level 5
- If they struggle at Level 3, de-escalate to Level 2, then Level 1
- 2-3 questions per sub-topic are sufficient to classify with confidence

### Confidence Rating

| Rating | Criteria |
|--------|----------|
| HIGH | 2+ consistent answers at the same level, performance matches across question types |
| MEDIUM | Mixed performance at a level, or only 1 data point |
| LOW | Insufficient data, contradictory signals, or learner seems to be guessing |

### Adaptive Flow

```
Start at Level 3
  ├── Correct → Try Level 4
  │     ├── Correct → Try Level 5
  │     │     ├── Correct → Try Level 6 (classify as 5-6)
  │     │     └── Incorrect → Classify as Level 4-5
  │     └── Incorrect → Classify as Level 3-4
  └── Incorrect → Try Level 2
        ├── Correct → Classify as Level 2-3
        └── Incorrect → Try Level 1
              ├── Correct → Classify as Level 1-2
              └── Incorrect → Classify as Level 0 (no prior knowledge)
```

---

## Question Templates by Bloom's Level

### Level 1: Remember

**Purpose**: Can the learner recall basic facts, terms, and syntax?

Templates:
- "What keyword is used to [action] in [language]?"
- "Name the [concept] that [description]."
- "What does the [term] stand for?"
- "List the [number] types of [category] in [language/framework]."
- "What is the default value of [type] in [language]?"

Programming examples:
- "What keyword creates a constant in JavaScript?"
- "Name three HTTP methods."
- "What does ORM stand for?"

### Level 2: Understand

**Purpose**: Can the learner explain concepts in their own words?

Templates:
- "Explain in your own words what [concept] does."
- "What is the difference between [concept A] and [concept B]?"
- "Why would you use [technique] instead of [alternative]?"
- "Read this code and describe what it does without running it."
- "What would happen if you removed [line/element] from this code?"

Programming examples:
- "Explain the difference between `let` and `const`."
- "Read this function and describe what it returns."
- "Why would you use a hash map instead of an array here?"

### Level 3: Apply

**Purpose**: Can the learner use knowledge in a guided context?

Templates:
- "Write a [function/class] that [requirement]."
- "Given this [data/scenario], write code to [task]."
- "Implement [pattern/algorithm] for [specific case]."
- "Using [method/library], solve [problem]."
- "What is the output of this code?" (prediction)

Programming examples:
- "Write a function that returns the longest string in an array."
- "Implement a stack using an array."
- "What does this recursive function return when called with 5?"

### Level 4: Analyze

**Purpose**: Can the learner break apart problems and find structure?

Templates:
- "This code has a bug that appears when [condition]. Find it and explain why."
- "Compare the time complexity of these two approaches."
- "What test cases would you write to thoroughly test this function?"
- "Identify the design pattern used in this code."
- "Why does this code fail for [edge case]? Trace through the execution."

Programming examples:
- "This sorting function works for most inputs but fails for arrays with duplicates. Why?"
- "Compare using recursion vs iteration for this problem. What are the tradeoffs?"
- "What edge cases should we test for a function that parses URLs?"

### Level 5: Evaluate

**Purpose**: Can the learner make and defend judgments?

Templates:
- "Given these two implementations, which is better and why?"
- "Critique this code for [quality: readability/performance/maintainability]."
- "Is [pattern/approach] appropriate for this use case? Justify."
- "What are the tradeoffs of [decision] in this architecture?"
- "Review this pull request. What would you approve, request changes on, and why?"

Programming examples:
- "Here are two implementations of a cache. Which would you use in production and why?"
- "Is using inheritance the right choice here, or would composition be better?"
- "This function works but takes 200ms. Is that acceptable? What factors matter?"

### Level 6: Create

**Purpose**: Can the learner produce original work from requirements?

Templates:
- "Design a [system/API/module] that handles [requirements]."
- "Architect a solution for [problem] considering [constraints]."
- "Build a [project] from scratch. You decide the approach."
- "Create a [library/tool] that abstracts [pattern]."
- "How would you design [feature] if you were starting from zero?"

Programming examples:
- "Design an API for a bookmarking service. Define the endpoints, data model, and auth strategy."
- "Build a CLI tool that monitors file changes and runs tests automatically."
- "How would you architect a notification system that supports email, SMS, and push?"

---

## Exercise Templates by Level

### Beginner (Bloom's 1-2)

**Structure**: Maximum scaffolding. Starter files with TODO comments, clear instructions, expected output provided, test file included.

```
exercises/01-topic-name/
├── README.md          # Instructions with examples
├── starter.ext        # Code with TODO comments marking what to fill in
├── test.ext           # Tests that verify the solution
└── expected-output.md # What success looks like
```

### Intermediate (Bloom's 3-4)

**Structure**: Requirements provided, no starter code. Test cases given. Learner creates files.

```
exercises/05-topic-name/
├── README.md          # Requirements, constraints, test cases
└── test.ext           # Tests the learner's code must pass
```

### Advanced (Bloom's 5-6)

**Structure**: Problem statement only. Learner decides everything.

```
exercises/09-topic-name/
└── README.md          # Problem statement, success criteria, no hints
```

---

## Mastery Measurement

### Per-Concept Tracking

Each concept is tracked independently with:
- Current Bloom's level (1-6)
- Leitner box (1-5)
- Number of quiz attempts at each level
- Last assessment date
- Feynman check (passed/not attempted)

### Progression Gates

Before advancing from one module to the next, the learner must demonstrate:

| Gate Level | Requirement |
|-----------|-------------|
| Minimum | Bloom's Level 3 on all prerequisite concepts |
| Recommended | Bloom's Level 4 on core concepts, Level 3 on supporting concepts |
| Mastery | Bloom's Level 4+ on all concepts, Leitner Box 3+ |

Gates are NOT punitive. If a learner is not ready, frame it as: "There are a few seeds that need more time to root. Let us strengthen them so the next module clicks."

### Multi-Format Assessment

Learners demonstrate understanding in different ways. Accept all valid demonstrations:
- Writing code that works
- Explaining a concept clearly (Feynman)
- Debugging someone else's code
- Designing a solution (whiteboard-style)
- Teaching the concept to the tutor

### Avoiding False Positives

- Multiple choice tests recognition, not recall. Prefer open-ended retrieval.
- "Does this look right?" is weak. "Write it from scratch" is strong.
- One correct answer could be luck. Require consistency (2-3 correct at the same level).
- If the learner uses jargon they cannot define simply, they are at Level 1 (Remember), not Level 2 (Understand).

---

## Assessment Tone

Always reference the `teaching-personality` knowledge base. Assessments are explorations, not tests.

- Frame as: "Let me understand where you are so I can guide you well"
- Not as: "Let me test you to see if you pass"
- If the learner says "I do not know," respond: "That is perfectly fine. That tells me exactly where we should focus. Knowing what you do not know is the first step."
- Never make the learner feel graded. There are no grades. There is only "where you are" and "where you are headed."
