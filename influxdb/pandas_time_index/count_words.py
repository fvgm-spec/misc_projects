#!/usr/bin/env python3
import re

with open('pandas_time_index_tutorial.md', 'r') as f:
    content = f.read()

# Remove code blocks
content_no_code = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
content_no_code = re.sub(r'`[^`]*`', '', content_no_code)

# Remove markdown formatting
content_no_code = re.sub(r'^#+\s*', '', content_no_code, flags=re.MULTILINE)
content_no_code = re.sub(r'\*\*([^*]+)\*\*', r'\1', content_no_code)
content_no_code = re.sub(r'\*([^*]+)\*', r'\1', content_no_code)

# Count words
words = content_no_code.split()
word_count = len(words)

print(f'Word count (excluding code): {word_count}')
print(f'Target range: 1,200-1,400 words')
print(f'Status: {"✅ Within range" if 1200 <= word_count <= 1400 else "❌ Outside range"}')

if word_count < 1200:
    print(f'Need to add: {1200 - word_count} words')
elif word_count > 1400:
    print(f'Need to remove: {word_count - 1400} words')
