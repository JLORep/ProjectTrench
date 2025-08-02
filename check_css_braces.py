import re

with open('streamlit_app.py', 'r', encoding='utf-8') as f:
    content = f.read()
    
# Extract CSS blocks
css_blocks = re.findall(r'<style>(.*?)</style>', content, re.DOTALL)

for i, css in enumerate(css_blocks):
    open_braces = css.count('{')
    close_braces = css.count('}')
    print(f'CSS Block {i+1}: {open_braces} open braces, {close_braces} close braces')
    if open_braces != close_braces:
        print(f'  MISMATCH: {open_braces - close_braces} extra open braces')
        
        # Find approximate location of mismatch
        lines = css.split('\n')
        running_balance = 0
        for j, line in enumerate(lines):
            opens = line.count('{')
            closes = line.count('}')
            running_balance += opens - closes
            if running_balance < 0:
                print(f'  Possible issue at line {j+1}: {line.strip()[:50]}...')