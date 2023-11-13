from prompt_toolkit import PromptSession
from prompt_toolkit.lexers import PygmentsLexer
from pygments import highlight
from pygments.token import Token
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalFormatter
import re

# Define a dictionary to map placeholders to colors
custom_colors = {
    '§lx.Comment§': '#808080',   # Gray for comments
    '§lx.String§': '#FF0000',    # Red for strings
    '§lx.Keyword§': '#00FF00',   # Green for flags
    '§lx.Name.Function§': '#0000FF',  # Blue for commands
    '§lx.Number§': '#FFA500',    # Orange for expressions
    '§lx.Operator§': '#0070BB',  # Blue for operators
    '§lx.Punctuation§': '#DD1144',  # Pink for parentheses, brackets, etc.
}

# Regular expression to match placeholders in the form §lx.<type>§
placeholder_regex = re.compile(r'§lx\.(.*?)§')

class CustomLexer(PygmentsLexer):
    def get_tokens(self, cli, text):
        tokens = list(super().get_tokens(cli, text))
        colored_tokens = []

        for token, value in tokens:
            # Replace placeholders with colors
            if token == Token.Text:
                value = placeholder_regex.sub(
                    lambda match: custom_colors.get(f'§lx.{match.group(1)}§', match.group(0)),
                    value
                )
            colored_tokens.append((token, value))
        return colored_tokens

def main():
    session = PromptSession(lexer=CustomLexer())

    while True:
        try:
            code = session.prompt("Enter Python code: ")
            if code.strip() == 'exit':
                break

            # Use Pygments to highlight the code
            highlighted_code = highlight(code, get_lexer_by_name("python"), TerminalFormatter())
            print(highlighted_code)
        except KeyboardInterrupt:
            pass
        except EOFError:
            break

if __name__ == '__main__':
    main()
