# Todo

## Plan
Build foundation modules first (configuration and utilities), then implement core text processing capabilities, followed by markdown formatting with math support, and finally the LLM bridge system with multi-model routing. Focus on the most user-facing features that define this project's academic assistance capabilities.

## Tasks
- [x] Task 1: Implement configuration management system that loads settings from environment variables, private config, and default config files with proper priority (env > private > default) and type conversion (config_loader.py + tests)
- [x] Task 2: Implement API key pattern validation for different providers (OpenAI, Azure, API2D, Cohere) with regex matching, key selection based on model type, and multi-key load balancing (key_pattern_manager.py + tests)
- [x] Task 3: Implement text masking utilities for language-based string transformation that allows conditional text rendering based on detected language (text_mask.py + tests)
- [x] Task 4: Implement colorful logging utilities with styled console output for different log levels (colorful.py + tests)
- [x] Task 5: Implement markdown-to-HTML conversion with code highlighting, LaTeX math formula support via tex2mathml, equation detection, and indent fixing (markdown_format.py + tests)
- [x] Task 6: Implement core text processing functions that generate prompts for academic polishing, grammar checking, translation, code explanation, and mind map generation (core_functional.py + tests)
- [x] Task 7: Implement main toolbox utilities including chat history writer, proxy context manager, file utilities, time helpers, and UI update generators (toolbox.py + tests)
- [x] Task 8: Implement a basic LLM bridge interface with model info registry, token counting, endpoint management, and predict functions for OpenAI-compatible APIs (llm_bridge.py + tests)
- [x] Task 9: Implement a simple plugin system that registers and dispatches function plugins with hot reload support (plugin_system.py + tests)
- [x] Task 10: Integrate all modules and implement the main entry point that ties configuration, LLM, plugins, and UI utilities together (main_integration.py + tests)
