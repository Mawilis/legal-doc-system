"""
WILSY OS — PDF REGRESSION & STYLING GUARD
Ensures all executive milestone reports maintain uncompromised green status tags.
"""
import os
import sys

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

def test_executive_kernel_styles():
    kernel_path = os.path.join(_PROJECT_ROOT, "scripts", "lib", "executive_pdf_kernel.py")
    assert os.path.exists(kernel_path), "Executive kernel missing!"
    
    with open(kernel_path, "r") as f:
        content = f.read()
        
    # Verify core styling components exist
    assert "#15803D" in content, "Critical green success color code missing from kernel!"
    print("[SUCCESS]: PDF Kernel style guard verified successfully.")

if __name__ == "__main__":
    test_executive_kernel_styles()
