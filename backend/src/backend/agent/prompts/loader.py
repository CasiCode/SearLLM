import warnings
import os


DIRNAME = os.path.dirname(__file__)


class PromptLoader:
    def __init__(self, filename):
        self._filename = filename

    def filename(self):
        return self._filename

    def load_prompt(self) -> str:
        """
        Returns prompt as string.

        returns:
            String read from the prompt file
        """
        abs_path = os.path.join(DIRNAME, self._filename)
        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                return f.read()
        except OSError:
            warnings.warn(
                message="File not found, check the provided filname. Empty prompt loaded.",
                category=RuntimeWarning,
                stacklevel=3,
            )
            return ""
