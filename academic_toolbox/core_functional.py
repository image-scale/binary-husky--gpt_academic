"""
Core functional module providing academic text processing prompts.
Defines functions for academic polishing, translation, grammar checking,
code explanation, and mind map generation.
"""
from textwrap import dedent
from .text_mask import build_masked_string_langbased, apply_mask_langbased


def clear_line_break(text):
    """
    Remove line breaks from text for cleaner processing.

    Args:
        text: The input text

    Returns:
        Text with line breaks removed
    """
    if text is None:
        return None
    return text.replace('\n', ' ').replace('\r', ' ')


def get_core_functions():
    """
    Get the dictionary of core academic functions.

    Each function definition contains:
        - Prefix: Text added before user input (the prompt)
        - Suffix: Text added after user input
        - Color: Button color (optional, default "secondary")
        - Visible: Whether button is visible (optional, default True)
        - AutoClearHistory: Whether to clear chat history (optional, default False)
        - PreProcess: Preprocessing function for input (optional)
        - ModelOverride: Override model selection (optional)

    Returns:
        Dictionary mapping function names to their configurations
    """
    return {
        "Academic Polish": {
            "Prefix": build_masked_string_langbased(
                text_show_english=(
                    "Below is a paragraph from an academic paper. Polish the writing to meet the academic style, "
                    "improve the spelling, grammar, clarity, concision and overall readability. When necessary, rewrite the whole sentence. "
                    "Firstly, you should provide the polished paragraph (in English). "
                    "Secondly, you should list all your modification and explain the reasons to do so in markdown table."
                ),
                text_show_chinese=(
                    "作为一名中文学术论文写作改进助理，你的任务是改进所提供文本的拼写、语法、清晰、简洁和整体可读性，"
                    "同时分解长句，减少重复，并提供改进建议。请先提供文本的更正版本，然后在markdown表格中列出修改的内容，并给出修改的理由:"
                )
            ) + "\n\n",
            "Suffix": "",
            "Color": "secondary",
            "Visible": True,
            "AutoClearHistory": False,
            "PreProcess": None,
        },

        "Grammar Check": {
            "Prefix": (
                "Help me ensure that the grammar and the spelling is correct. "
                "Do not try to polish the text, if no mistake is found, tell me that this paragraph is good. "
                "If you find grammar or spelling mistakes, please list mistakes you find in a two-column markdown table, "
                "put the original text the first column, "
                "put the corrected text in the second column and highlight the key words you fixed. "
                "Finally, please provide the proofreaded text.\n\n"
                "Example:\n"
                "Paragraph: How is you? Do you knows what is it?\n"
                "| Original sentence | Corrected sentence |\n"
                "| :--- | :--- |\n"
                "| How **is** you? | How **are** you? |\n"
                "| Do you **knows** what **is** **it**? | Do you **know** what **it** **is** ? |\n\n"
                "Below is a paragraph from an academic paper. "
                "You need to report all grammar and spelling mistakes as the example before.\n\n"
            ),
            "Suffix": "",
            "PreProcess": clear_line_break,
        },

        "Chinese to English": {
            "Prefix": "Please translate following sentence to English:\n\n",
            "Suffix": "",
        },

        "English to Chinese": {
            "Prefix": "翻译成地道的中文：\n\n",
            "Suffix": "",
            "Visible": False,
        },

        "Academic Translation": {
            "Prefix": build_masked_string_langbased(
                text_show_chinese=(
                    "I want you to act as a scientific English-Chinese translator, "
                    "I will provide you with some paragraphs in one language "
                    "and your task is to accurately and academically translate the paragraphs only into the other language. "
                    "Do not repeat the original provided paragraphs after translation. "
                    "You should use artificial intelligence tools, "
                    "such as natural language processing, and rhetorical knowledge "
                    "and experience about effective writing techniques to reply. "
                    "I'll give you my paragraphs as follows, tell me what language it is written in, and then translate:"
                ),
                text_show_english=(
                    "你是经验丰富的翻译，请把以下学术文章段落翻译成中文，"
                    "并同时充分考虑中文的语法、清晰、简洁和整体可读性，"
                    "必要时，你可以修改整个句子的顺序以确保翻译后的段落符合中文的语言习惯。"
                    "你需要翻译的文本如下："
                )
            ) + "\n\n",
            "Suffix": "",
        },

        "Explain Code": {
            "Prefix": "请解释以下代码：\n```\n",
            "Suffix": "\n```\n",
        },

        "Mind Map": {
            "Prefix": '"""\n\n',
            "Suffix": dedent("\n\n" + '''
                """

                使用mermaid flowchart对以上文本进行总结，概括上述段落的内容以及内在逻辑关系，例如：

                以下是对以上文本的总结，以mermaid flowchart的形式展示：
                ```mermaid
                flowchart LR
                    A["节点名1"] --> B("节点名2")
                    B --> C{"节点名3"}
                    C --> D["节点名4"]
                    C --> |"箭头名1"| E["节点名5"]
                    C --> |"箭头名2"| F["节点名6"]
                ```

                注意：
                （1）使用中文
                （2）节点名字使用引号包裹，如["Laptop"]
                （3）`|` 和 `"`之间不要存在空格
                （4）根据情况选择flowchart LR（从左到右）或者flowchart TD（从上到下）
            '''),
        },

        "Bibliography to BibTeX": {
            "Prefix": (
                "Here are some bibliography items, please transform them into bibtex style. "
                "Note that, reference styles maybe more than one kind, you should transform each item correctly. "
                "Items need to be transformed:\n\n"
            ),
            "Suffix": "",
            "Visible": False,
        },
    }


def handle_core_functionality(func_name, inputs, history, functions=None):
    """
    Apply core functionality transformation to user inputs.

    Args:
        func_name: Name of the function to apply
        inputs: User input text
        history: Chat history list
        functions: Optional custom functions dict (for testing). If None, uses get_core_functions()

    Returns:
        Tuple of (transformed_inputs, updated_history)

    Raises:
        KeyError: If func_name is not found in functions
    """
    if functions is None:
        functions = get_core_functions()

    if func_name not in functions:
        raise KeyError(f"Function '{func_name}' not found in core functions")

    func_config = functions[func_name]

    # Apply preprocessing if defined
    if "PreProcess" in func_config and func_config["PreProcess"] is not None:
        inputs = func_config["PreProcess"](inputs)

    # Build the transformed input with prefix and suffix
    prefix = func_config.get("Prefix", "")
    suffix = func_config.get("Suffix", "")
    transformed = prefix + inputs + suffix

    # Apply language-based mask transformation
    transformed = apply_mask_langbased(transformed, lang_reference=inputs)

    # Handle auto-clear history
    if func_config.get("AutoClearHistory", False):
        history = []

    return transformed, history


def get_function_names(visible_only=True):
    """
    Get list of available function names.

    Args:
        visible_only: If True, only return visible functions

    Returns:
        List of function names
    """
    functions = get_core_functions()
    if visible_only:
        return [name for name, config in functions.items()
                if config.get("Visible", True)]
    return list(functions.keys())


def get_function_config(func_name):
    """
    Get configuration for a specific function.

    Args:
        func_name: Name of the function

    Returns:
        Function configuration dictionary

    Raises:
        KeyError: If function not found
    """
    functions = get_core_functions()
    if func_name not in functions:
        raise KeyError(f"Function '{func_name}' not found")
    return functions[func_name]
