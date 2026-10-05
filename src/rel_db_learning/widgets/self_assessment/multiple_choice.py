"""Multiple-choice self-assessment widget for REL_DB_LEARNING notebooks.

Renders a question with radio-button options and a check button. Students
can answer multiple times; feedback is shown in English after each attempt.

Used in modules 01, 02, and 03. Not used in module 04.
"""

from __future__ import annotations

from typing import List, Optional

import ipywidgets as widgets
from IPython.display import display


def multiple_choice(
    question: str,
    options: List[str],
    correct_index: int,
    explanation: Optional[str] = None,
) -> None:
    """Display a multiple-choice question with interactive feedback.

    Parameters
    ----------
    question : str
        Question text. May contain Unicode algebra symbols.
    options : list of str
        Answer choices shown as radio buttons.
    correct_index : int
        Zero-based index of the correct option in ``options``.
    explanation : str, optional
        Additional explanation shown after the student answers.
    """
    question_html = widgets.HTML(
        value=f"<div style='font-size:1em; margin-bottom:8px;'>{question}</div>"
    )
    radio = widgets.RadioButtons(
        options=options,
        layout=widgets.Layout(width="100%"),
    )
    button = widgets.Button(
        description="Check",
        button_style="primary",
        layout=widgets.Layout(width="120px"),
    )
    output = widgets.Output()

    def on_check(_btn: widgets.Button) -> None:
        output.clear_output()
        selected = radio.index
        with output:
            if selected == correct_index:
                msg = "<span style='color:#2e7d32; font-weight:bold;'>✓ Correct</span>"
            else:
                correct_text = options[correct_index]
                msg = (
                    f"<span style='color:#c62828; font-weight:bold;'>✗ Incorrect.</span>"
                    f" The correct answer is: <em>{correct_text}</em>"
                )
            html_parts = [f"<div style='margin:6px 0;'>{msg}</div>"]
            if explanation:
                html_parts.append(
                    f"<div style='margin-top:4px; color:#555;'>{explanation}</div>"
                )
            display(widgets.HTML(value="".join(html_parts)))

    button.on_click(on_check)
    display(widgets.VBox([question_html, radio, button, output]))
