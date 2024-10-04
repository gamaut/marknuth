import re
import sys

def parse_markdown(content):
    pattern = re.compile(
        r'```(?P<lang>\w+)?\s*<<(?P<name>.*?)>>(?P<operator>\+?=)\n(?P<code>.*?)\n```', re.DOTALL)
    chunks = {}
    for match in pattern.finditer(content):
        lang = match.group('lang')
        name = match.group('name').strip()
        operator = match.group('operator')
        code = match.group('code').strip()
        if name not in chunks:
            chunks[name] = {'code_parts': [], 'lang': lang}
        if operator == '=':
            if chunks[name]['code_parts']:
                raise ValueError(f"Chunk '{name}' redefined using '=' after it has been defined.")
            chunks[name]['code_parts'].append(code)
        elif operator == '+=':
            chunks[name]['code_parts'].append(code)
        else:
            raise ValueError(f"Unknown operator '{operator}' in chunk '{name}'")
    return chunks

def resolve_chunk(name, chunks, resolved, seen):
    if name in resolved:
        return resolved[name]
    if name in seen:
        seen_chain = ' -> '.join(seen + [name])
        raise ValueError(f"Circular reference detected: {seen_chain}")
    if name not in chunks:
        raise ValueError(f"Undefined chunk: {name}")
    seen.append(name)
    code_parts = []
    for part in chunks[name]['code_parts']:
        code = re.sub(
            r'<<(?P<ref_name>.*?)>>',
            lambda m: resolve_chunk(m.group('ref_name').strip(), chunks, resolved, seen),
            part)
        code_parts.append(code)
    seen.pop()
    resolved[name] = '\n'.join(code_parts)
    return resolved[name]

def assemble_code(chunks, main_chunk='Main Program'):
    resolved = {}
    code = resolve_chunk(main_chunk, chunks, resolved, [])
    return code

def main(input_file, output_file, main_chunk='Main Program'):
    with open(input_file, 'r') as f:
        content = f.read()
    chunks = parse_markdown(content)
    try:
        final_code = assemble_code(chunks, main_chunk)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    with open(output_file, 'w') as f:
        f.write(final_code)

if __name__ == '__main__':
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python marknuth.py <input.md> <output> [<main chunk name>]")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    main_chunk = sys.argv[3] if len(sys.argv) == 4 else 'Main Program'
    main(input_file, output_file, main_chunk)
