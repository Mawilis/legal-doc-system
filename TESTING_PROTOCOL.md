# 🏛️ Wilsy OS - Testing & Integrity Protocol

## 🚨 Critical Architecture Warning: Canvas Testing
The `Sovereign_Covenant_Modal` uses forensic pixel-detection to enable the "Seal" button.

**The JSDOM Trap:** Vitest/JSDOM does not render pixels. `getImageData()` will return `0` even if `fireEvent` is used.

**The Protocol:**
1.  **Direct State Trigger:** The `draw` function in the component must include a `hasSigned` toggle on movement specifically for the test environment.
2.  **Stroke Simulation:** Tests must fire multiple `mouseMove` events to simulate a "complex" signature, as single clicks may be ignored by the component's internal debounce logic.

## 🕒 Timing & Animations
The Sovereign Anchor sequence (`handleSealSequence`) uses a `setInterval` to simulate high-precision processing.
- **Test Requirement:** Use `findBy` queries with a minimum `timeout: 5000` to allow the progress bar to finish before checking for the next UI state.

## 🧪 Common Error Resolutions
| Error | Cause | Fix |
| :--- | :--- | :--- |
| `Expression expected` | Rollup AST Parse failure | Simplify JSX; check for hidden special characters or broken template literals. |
| `expect(...).not.toBeDisabled()` | Canvas remains "blank" in JSDOM | Ensure the `draw` function updates state on movement, not just on `mouseUp`. |
| `Chart width/height < 0` | JSDOM lack of layout engine | Expected noise. Can be ignored or mocked using `ResizeObserver`. |

---
*Last Updated: March 14, 2026 | Authority: System Admin*
