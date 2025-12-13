import subprocess


class CodeExecutor:
    TIMEOUT = 5

    @staticmethod
    def execute_code(code: str, test_input: str) -> tuple:
        try:
            result = subprocess.run(
                ['python', '-c', code],
                input=test_input,
                capture_output=True,
                text=True,
                timeout=CodeExecutor.TIMEOUT
            )

            if result.returncode != 0:
                return (False, result.stdout, result.stderr)

            return (True, result.stdout, "")

        except subprocess.TimeoutExpired:
            return (False, "", "Time Limit Exceeded")
        except Exception as e:
            return (False, "", str(e))

    @staticmethod
    def classify_failure(code: str, test_outputs: list) -> tuple:
        syntax_error = CodeExecutor._check_syntax(code)
        if syntax_error:
            return ("syntax", f"Syntax error: {syntax_error}")

        for test_input, expected_output in test_outputs:
            success, actual_output, error = CodeExecutor.execute_code(code, test_input)

            if not success:
                if "Time Limit Exceeded" in error:
                    return ("tle", "Code runs too slowly (timeout after 5s)")
                return ("runtime", f"Runtime error: {error}")

            actual_clean = actual_output.strip()
            expected_clean = expected_output.strip()

            if actual_clean != expected_clean:
                diff = CodeExecutor._get_diff_summary(actual_clean, expected_clean)
                return ("wrong_answer", diff)

        return ("accepted", "All tests passed")

    @staticmethod
    def _check_syntax(code: str) -> str:
        try:
            compile(code, '<string>', 'exec')
            return ""
        except SyntaxError as e:
            return f"Line {e.lineno}: {e.msg}"

    @staticmethod
    def _get_diff_summary(actual: str, expected: str) -> str:
        actual_lines = actual.split('\n')
        expected_lines = expected.split('\n')

        if len(actual_lines) != len(expected_lines):
            return f"Output has {len(actual_lines)} lines but expected {len(expected_lines)} lines"

        for i, (a, e) in enumerate(zip(actual_lines, expected_lines)):
            if a != e:
                return f"Line {i + 1}: got '{a[:40]}' but expected '{e[:40]}'"

        return "Output mismatch (format issue)"