# 🚨 HTML Rendering Error - Critical Gotchas

**CRITICAL**: This error has occurred multiple times and keeps coming back!

## The Problem
Raw HTML displaying in dashboard tabs instead of properly rendered content.

## Root Causes

### 1. **F-String Format Specification Errors**
```python
# ❌ WRONG - This will cause HTML to display as text
${coin.get('current_volume_24h') or 0:,.0f}

# ✅ CORRECT - Use default parameter in .get()
${coin.get('current_volume_24h', 0):,.0f}
```

### 2. **Unclosed F-String Templates**
```python
# ❌ WRONG - F-string not properly closed
card_html = f"""<div class="card">
    {content}
</div>
<style>
.card { color: red; }
</style>"""

# ✅ CORRECT - Close f-string before adding non-templated content
card_html = f"""<div class="card">
    {content}
</div>"""

style_html = """<style>
.card { color: red; }
</style>"""
```

### 3. **Mixed CSS in F-Strings with Double Braces**
```python
# ❌ WRONG - Can cause parsing issues
f"""<style>
.card:hover {{
    background: {color};
}}
</style>"""

# ✅ CORRECT - Separate static CSS from dynamic content
hover_styles = """<style>
.card:hover {
    background: #10b981;
}
</style>"""
```

## Quick Diagnosis

When you see raw HTML in the dashboard:

1. **Check Streamlit Logs** for syntax errors
2. **Search for** `${` patterns in the code
3. **Look for** f-strings containing CSS with `{{`
4. **Verify** all f-strings are properly closed with `"""`

## Prevention Checklist

Before deployment, always:
- [ ] Run `python validate_code.py`
- [ ] Check for `or` operators in f-string format specs
- [ ] Ensure CSS is separated from f-string templates
- [ ] Verify all HTML strings are properly escaped
- [ ] Test locally before pushing

## Common Locations

These errors typically occur in:
- `streamlit_app.py` - Coin cards (Tab 2)
- `streamlit_app.py` - Hunt Hub integration (Tab 3)
- Any dynamic HTML generation with f-strings

## Emergency Fix

If you encounter this error:
```bash
# 1. Search for problematic patterns
grep -n "\${.*or.*:.*}" streamlit_app.py

# 2. Run smart validation
python validate_html_css_smart.py

# 3. Test specific tabs
python test_specific_tab.py --tab=2
```

## Historical Occurrences

1. **2025-08-02 14:21** - Coin card volume formatting
2. **2025-08-02 17:32** - Hunt Hub HTML escaping
3. **2025-08-02 19:09** - F-string template closure

---

**Remember**: This error will hide ALL features in affected tabs. Fix immediately when detected!