import "../scss/_persistent-pad.scss";
import { useState, useEffect } from "react";
import Col from "react-bootstrap/Col";

export default function PersistentPad({ equation, onHighlightChange, side }) {
  const [highlightedText, setHighlightedText] = useState("");
  const [lastClickTime, setLastClickTime] = useState(0);
  const [selectionRange, setSelectionRange] = useState({ start: 0, end: 0 });

  const handelClick = () => {
    const currentTime = new Date().getTime();
    const clickDuration = currentTime - lastClickTime;

    if (clickDuration < 300) {
      handelSelection();
    } else {
      highlightSelection();
    }

    setLastClickTime(currentTime);
  };

  const highlightSelection = () => {
    const selection = window.getSelection();
    const range = selection.getRangeAt(0);
    setSelectionRange({ start: range.startOffset, end: range.endOffset });
    const selectedText = range.toString();
    setHighlightedText(selectedText);
    onHighlightChange(getStartIndex(selectedText));
  };

  const handelSelection = () => {
    try {
      setHighlightedText("");
      const range = window.getSelection().getRangeAt(0);
      const startOffset = range.startOffset;
      const endOffset = range.endOffset;

      const selectionRange = { start: startOffset, end: endOffset };
      handelHighlight(selectionRange);
    } catch (error) {
      console.error("Error while highlighting selection: ", error);
    }
  };

  const handelHighlight = (selectionRange) => {
    const selectedPart = findSelectionParenthesis(selectionRange);
    if (!checkParenthesesConsistency(selectedPart)) {
      const highlighted = checkAndGetQuotient(balanceParentheses(selectedPart));
      setHighlightedText(highlighted);
      onHighlightChange(getStartIndex(highlighted));
      setSelectionRange({
        start: getStartIndex(highlighted),
        end: getEndIndex(highlighted)
      });
    } else {
      const highlighted = checkAndGetQuotient(selectedPart);
      setHighlightedText(highlighted);
      onHighlightChange(getStartIndex(highlighted));
      setSelectionRange({
        start: getStartIndex(highlighted),
        end: getEndIndex(highlighted)
      });
    }
  };

  const getStartIndex = (selectedText) => {
    return equation.indexOf(selectedText);
  };

  const getEndIndex = (selectedText) => {
    return getStartIndex(selectedText) + selectedText.length;
  };

  const checkAndGetQuotient = (selectedText) => {
    const start = equation.indexOf(selectedText);
    const end = start + selectedText.length;

    if (equation[start - 1] === "'") {
      const quotient = equation.substring(start - 1, end);
      return quotient;
    } else {
      return selectedText;
    }
  };

  const findSelectionParenthesis = (selectionRange) => {
    const start = selectionRange.start;
    const end = selectionRange.end;
    let openParenthesisIndex = -1;
    let closeParenthesisIndex = -1;

    for (let i = start; i >= 0; i--) {
      if (equation[i] === "(") {
        openParenthesisIndex = i;
        break;
      }
    }

    for (let i = end; i < equation.length; i++) {
      if (equation[i] === ")") {
        closeParenthesisIndex = i;
        break;
      }
    }

    if (openParenthesisIndex !== -1 && closeParenthesisIndex !== -1) {
      return equation.substring(
        openParenthesisIndex,
        closeParenthesisIndex + 1
      );
    }
  };

  const checkParenthesesConsistency = (selectedText) => {
    if (!selectedText) {
      return;
    }

    const stack = [];

    for (let i = 0; i < selectedText.length; i++) {
      const char = selectedText[i];
      if (char === "(") {
        stack.push(char);
      } else if (char === ")") {
        if (stack.length === 0) {
          return false; // More closing parentheses than opening ones
        }
        stack.pop();
      }
    }

    return stack.length === 0; // Return true if stack is empty, false otherwise
  };

  const balanceParentheses = (selectedText) => {
    const stack = [];

    // Find the starting index of the selected text in the equation
    const startIndex = equation.indexOf(selectedText);
    if (startIndex === -1) {
      // Selected text not found in equation
      return selectedText;
    }

    // Find the start index of the expression containing the selected text
    let start = startIndex;
    while (start > 0 && equation[start] !== "(") {
      start--;
    }

    // Find the end index of the expression containing the selected text
    let end = startIndex + selectedText.length;
    while (end < equation.length && equation[end] !== ")") {
      end++;
    }

    // Extract the entire expression containing the selected text
    let expression = equation.substring(start, end + 1);

    if (!checkParenthesesConsistency(expression)) {
      expression = balanceParentheses(expression);
    }

    // Push opening parentheses onto the stack
    for (let i = 0; i < expression.length; i++) {
      const char = expression[i];
      if (char === "(") {
        stack.push(char);
      } else if (char === ")") {
        if (stack.length === 0) {
          // Add an opening parenthesis to balance
          expression = expression.slice(0, i) + "(" + expression.slice(i);
          stack.push("(");
        } else {
          stack.pop();
        }
      }
    }

    // Add missing closing parentheses to balance
    while (stack.length > 0) {
      expression += ")";
      stack.pop();
    }
    return expression;
  };

  const clearHighlight = (e) => {
    e.preventDefault();
    setHighlightedText("");

    const savedHighlights = JSON.parse(sessionStorage.getItem("highlights"));
    const newHighlights = savedHighlights.filter(
      (highlight) =>
        !(highlight.equation === equation && highlight.side === side)
    );
    sessionStorage.setItem("highlights", JSON.stringify(newHighlights));
  };

  const replaceSelection = (selectionRange, replacement) => {
    const start = selectionRange.start;
    const end = selectionRange.end;
    const beforeSelection = equation.substring(0, start);
    const afterSelection = equation.substring(end);
    return (
      beforeSelection +
      `<span class="highlight">${replacement}</span>` +
      afterSelection
    );
  };

  useEffect(() => {
    const saveHighlightToSession = (highlightedText) => {
      const savedHighlights = JSON.parse(
        sessionStorage.getItem("highlights") || "[]"
      );

      savedHighlights.forEach((highlight, index) => {
        if (highlight.equation === equation && highlight.side === side) {
          savedHighlights.splice(index, 1);
        }
      });

      savedHighlights.push({ equation, highlightedText, side, selectionRange });
      sessionStorage.setItem("highlights", JSON.stringify(savedHighlights));
    };

    if (highlightedText) {
      saveHighlightToSession(highlightedText);
    }
  }, [highlightedText, equation, side, selectionRange]);

  useEffect(() => {
    const savedHighlights = JSON.parse(
      sessionStorage.getItem("highlights") || "[]"
    );

    savedHighlights.forEach((highlight) => {
      if (highlight.equation === equation && highlight.side === side) {
        setHighlightedText(highlight.highlightedText);
        setSelectionRange(highlight.selectionRange);
      }
    });
  }, [equation, side]);

  return (
    <Col xs={8}>
      <p
        onClick={handelClick}
        onContextMenu={clearHighlight}
        dangerouslySetInnerHTML={{
          __html: highlightedText
            ? replaceSelection(selectionRange, highlightedText)
            : equation
        }}
        className="pad"
      />
    </Col>
  );
}
