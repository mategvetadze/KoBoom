import difflib


class SolutionAnalyzer:
    @staticmethod
    def analyze_mistake(user_code: str, correct_code: str, failure_type: str) -> str:
        if failure_type == "syntax":
            return "Syntax error in code structure"

        if failure_type == "tle":
            return "Algorithm is too slow; likely nested loops or inefficient approach"

        if failure_type == "runtime":
            return "Code crashes; check array bounds, division by zero, or null references"

        user_lines = [l.strip() for l in user_code.split('\n') if l.strip() and not l.strip().startswith('#')]
        correct_lines = [l.strip() for l in correct_code.split('\n') if l.strip() and not l.strip().startswith('#')]

        matcher = difflib.SequenceMatcher(None, user_lines, correct_lines)

        mistakes = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'insert':
                missing_lines = correct_lines[j1:j2]
                missing_text = ' '.join(missing_lines)

                keywords = ['set(', 'dict', 'visited', 'sorted', 'reversed', 'max(', 'min(', 'for', 'while', 'if']
                if any(kw in missing_text for kw in keywords) and len(missing_text) < 80:
                    mistakes.append(f"Missing key step: {missing_text[:70]}")

            elif tag == 'replace':
                user_section = ' '.join(user_lines[i1:i2])
                correct_section = ' '.join(correct_lines[j1:j2])
                if len(user_section) < 80 and len(correct_section) < 80:
                    mistakes.append("Logic differs from correct approach")

        if mistakes:
            return mistakes[0]

        return "Logic error; trace through with a sample input step-by-step"
