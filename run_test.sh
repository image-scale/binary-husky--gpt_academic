#!/bin/bash
set -eo pipefail

export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1
export CI=true
export MPLBACKEND=Agg

cd /workspace/gpt_academic
rm -rf .pytest_cache

pytest -v --tb=short -p no:cacheprovider \
  tests/ \
  --ignore=tests/init_test.py \
  --ignore=tests/test_utils.py \
  --ignore=tests/test_plugins.py \
  --ignore=tests/test_academic_conversation.py \
  --ignore=tests/test_anim_gen.py \
  --ignore=tests/test_bilibili_down.py \
  --ignore=tests/test_doc2x.py \
  --ignore=tests/test_embed.py \
  --ignore=tests/test_latex_auto_correct.py \
  --ignore=tests/test_llms.py \
  --ignore=tests/test_markdown.py \
  --ignore=tests/test_markdown_format.py \
  --ignore=tests/test_media.py \
  --ignore=tests/test_python_auto_docstring.py \
  --ignore=tests/test_rag.py \
  --ignore=tests/test_safe_pickle.py \
  --ignore=tests/test_save_chat_to_html.py \
  --ignore=tests/test_searxng.py \
  --ignore=tests/test_social_helper.py \
  --ignore=tests/test_tts.py \
  --ignore=tests/test_vector_plugins.py

