"""
Fix app.py to handle missing hmmlearn gracefully
"""
import re

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the try-except block for hmmlearn check
old_pattern = r'''    # Check for hmmlearn
    try:
        import hmmlearn
        HMM_AVAILABLE = True
    except ImportError:
        HMM_AVAILABLE = False
        st.warning\("⚠️ hmmlearn not installed. Model training disabled."\)

    if HMM_AVAILABLE:'''

new_text = '''    # Display HMM availability status
    if not HMM_AVAILABLE:
        st.warning("⚠️ hmmlearn not installed. Model training disabled.")
        st.info("Dashboard works without it! You can still view data and configure settings.")

    if HMM_AVAILABLE:'''

content = re.sub(old_pattern, new_text, content, flags=re.MULTILINE)

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] app.py fixed successfully!")
print("Now run: streamlit run app.py")
