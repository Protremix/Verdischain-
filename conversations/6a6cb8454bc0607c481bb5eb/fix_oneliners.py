#!/usr/bin/env python3
"""Fix broken one-liners in the web wallet HTML where // comments swallow code."""
import re

path = '/var/www/verdiscan/wallet/index.html'

with open(path) as f:
    lines = f.readlines()

fixed_count = 0
new_lines = []

for i, line in enumerate(lines):
    if len(line) < 200:
        new_lines.append(line)
        continue
    
    # For long lines, we need to split at // comments that are followed by code
    # But we need to be careful not to break:
    # - URLs (http://, https://)
    # - String literals containing //
    # - Regex literals containing //
    
    # Strategy: find // that are NOT inside strings/regex and NOT URLs
    # Then check if code follows the comment
    
    result = []
    j = 0
    in_string = None  # None, "'", '"', or '`'
    in_regex = False
    escaped = False
    
    while j < len(line):
        char = line[j]
        
        if escaped:
            result.append(char)
            escaped = False
            j += 1
            continue
        
        if char == '\\':
            result.append(char)
            escaped = True
            j += 1
            continue
        
        if in_string:
            if char == in_string:
                in_string = None
            result.append(char)
            j += 1
            continue
        
        if char in ('"', "'", '`'):
            in_string = char
            result.append(char)
            j += 1
            continue
        
        # Check for // comment (not URL)
        if char == '/' and j + 1 < len(line) and line[j + 1] == '/':
            # Check if it's a URL (http:// or https://)
            if j >= 4 and line[j-4:j] in ('http', 'ttp:'):
                result.append(char)
                j += 1
                continue
            if j >= 5 and line[j-5:j] in ('https', 'ttps:'):
                result.append(char)
                j += 1
                continue
            
            # This is a // comment - find the end of the comment text
            comment_start = j
            # Find the end of the "word" in the comment
            k = j + 2
            # Skip the comment text
            while k < len(line) and line[k] != '\n':
                # Check if code follows after the comment word
                # Look for patterns like: // Comment function() or // Comment const x
                if k + 1 < len(line):
                    rest = line[k:]
                    # Check if we've reached code keywords
                    # Pattern: space or word char followed by a function/const/etc keyword
                    code_patterns = [
                        r'(?:^|\s)(function\s)',
                        r'(?:^|\s)(const\s)',
                        r'(?:^|\s)(let\s)',
                        r'(?:^|\s)(var\s)',
                        r'(?:^|\s)(window\.)',
                        r'(?:^|\s)(async\s)',
                        r'(?:^|\s)(return\s)',
                        r'(?:^|\s)(if\s*\()',
                        r'(?:^|\s)(document\.)',
                        r'(?:^|\s)(await\s)',
                        r'(?:^|\s)(}\s*catch)',
                        r'(?:^|\s)(}\s*else)',
                        r'(?:^|\s)(}\s*function)',
                        r'(?:^|\s)(}\s*const)',
                        r'(?:^|\s)(}\s*let)',
                        r'(?:^|\s)(}\s*var)',
                        r'(?:^|\s)(}\s*window)',
                        r'(?:^|\s)(}\s*async)',
                        r'(?:^|\s)(}\s*return)',
                        r'(?:^|\s)(}\s*if)',
                        r'(?:^|\s)(}\s*document)',
                        r'(?:^|\s)(}\s*await)',
                    ]
                    
                    for pattern in code_patterns:
                        match = re.search(pattern, rest)
                        if match and match.start() < 100:  # Only if within 100 chars of //
                            # Split here: add newline before the code
                            comment_text = line[comment_start:k + match.start()]
                            # Find the actual comment text (without the code)
                            # Go back to find where the comment text ends
                            # The comment text is from // to just before the code keyword
                            actual_comment = line[comment_start:k + match.start()].rstrip()
                            code_part = line[k + match.start():]
                            
                            # Add the comment + newline
                            result_line = ''.join(result) + actual_comment + '\n'
                            new_lines.append(result_line)
                            fixed_count += 1
                            
                            # Now process the remaining code part recursively
                            remaining = line[k + match.start():]
                            # Add it as a new line (with proper indentation)
                            # Find indentation from the start of the original line
                            indent_match = re.match(r'^\s*', line)
                            indent = indent_match.group() if indent_match else '  '
                            # Process remaining as a new line
                            if len(remaining) > 200:
                                # Recursively process
                                # For simplicity, just add it and let the next iteration handle it
                                # But we need to add it to new_lines, not result
                                remaining_line = indent + remaining.lstrip()
                                # Process this remaining line in the next iteration
                                # by adding it back to a temp list
                                temp_lines = [remaining_line]
                                for tl in temp_lines:
                                    if len(tl) < 200:
                                        new_lines.append(tl)
                                    else:
                                        # Just add it - we've fixed the main break
                                        new_lines.append(tl)
                            else:
                                new_lines.append(indent + remaining.lstrip())
                            
                            # Break out of all loops
                            j = len(line)
                            result = []  # Clear result so we don't double-add
                            break
                    
                    if j == len(line):
                        break
                k += 1
            
            if j < len(line):
                # No code found after comment, add the rest as-is
                result.append(line[j])
                j += 1
            continue
        
        # Also split after } followed by function/const/etc on same line
        if char == '}' and j + 1 < len(line) and line[j + 1] not in (')', ']', '}', ';', ',', '.', '\n', '\r', ' '):
            # Check if it's followed by a keyword
            rest = line[j+1:]
            split_patterns = [
                r'^(function\s)',
                r'^(const\s)',
                r'^(let\s)',
                r'^(var\s)',
                r'^(window\.)',
                r'^(async\s)',
                r'^(return\s)',
                r'^(if\s*\()',
                r'^(document\.)',
                r'^(await\s)',
                r'^(catch)',
                r'^(else)',
                r'^(for\s*\()',
                r'^(try\s*\{)',
            ]
            for pattern in split_patterns:
                if re.match(pattern, rest):
                    result.append('}\n')
                    new_lines.append(''.join(result))
                    fixed_count += 1
                    result = []
                    # Add remaining as new line
                    indent_match = re.match(r'^\s*', line)
                    indent = indent_match.group() if indent_match else '  '
                    remaining = indent + rest.lstrip()
                    if len(remaining) > 200:
                        # Will be processed in next iteration if needed
                        new_lines.append(remaining)
                    else:
                        new_lines.append(remaining)
                    j = len(line)
                    break
            if j < len(line):
                result.append(char)
                j += 1
            continue
        
        result.append(char)
        j += 1
    
    if result:
        new_lines.append(''.join(result))

with open(path, 'w') as f:
    f.writelines(new_lines)

print(f'Fixed {fixed_count} broken one-liners')
print(f'Lines: {len(lines)} -> {len(new_lines)}')
