# Advanced markdown formatting

def format_io(self, y):
    """Format chatbot IO for display.

    Args:
        self: Ignored (can be None when called as unbound method)
        y: List of [user_message, assistant_message] pairs

    Returns:
        Formatted chatbot list
    """
    if y is None:
        return []

    # Return the chatbot list with basic formatting
    result = []
    for pair in y:
        if isinstance(pair, (list, tuple)) and len(pair) >= 2:
            user_msg = pair[0] if pair[0] else ""
            assistant_msg = pair[1] if pair[1] else ""
            result.append([user_msg, assistant_msg])
        else:
            result.append(pair)

    return result
