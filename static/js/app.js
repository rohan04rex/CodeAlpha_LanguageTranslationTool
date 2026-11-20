/**
 * CodeAlpha AI Internship - Task 1: Language Translation Tool
 * Client-Side Application Logic
 */

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const sourceText = document.getElementById("sourceText");
    const targetText = document.getElementById("targetText");
    const outputPlaceholder = document.getElementById("outputPlaceholder");
    const sourceLangSelect = document.getElementById("sourceLangSelect");
    const targetLangSelect = document.getElementById("targetLangSelect");
    const swapLanguagesBtn = document.getElementById("swapLanguagesBtn");
    const translateBtn = document.getElementById("translateBtn");
    const btnSpinner = document.getElementById("btnSpinner");
    const btnText = document.getElementById("btnText");
    const clearInputBtn = document.getElementById("clearInputBtn");
    const copyResultBtn = document.getElementById("copyResultBtn");
    const copyBtnText = document.getElementById("copyBtnText");
    const copyIconDefault = document.getElementById("copyIconDefault");
    const copyIconSuccess = document.getElementById("copyIconSuccess");
    const charCount = document.getElementById("charCount");
    const wordCount = document.getElementById("wordCount");
    const detectedBadge = document.getElementById("detectedBadge");
    const detectedLangName = document.getElementById("detectedLangName");
    const providerBadge = document.getElementById("providerBadge");
    const resultStats = document.getElementById("resultStats");
    const themeToggleBtn = document.getElementById("themeToggleBtn");
    const historyList = document.getElementById("historyList");
    const clearHistoryBtn = document.getElementById("clearHistoryBtn");
    const toastContainer = document.getElementById("toastContainer");
    const sampleTriggers = document.querySelectorAll(".sample-trigger");

    let isTranslating = false;
    let lastDetectedCode = null;

    // --- 1. Theme Management ---
    const savedTheme = localStorage.getItem("codealpha_theme") || "dark-theme";
    document.body.className = savedTheme;

    themeToggleBtn.addEventListener("click", () => {
        const isDark = document.body.classList.contains("dark-theme");
        const nextTheme = isDark ? "light-theme" : "dark-theme";
        document.body.className = nextTheme;
        localStorage.setItem("codealpha_theme", nextTheme);
        showToast(`Switched to ${isDark ? "Light" : "Dark"} mode`, "info");
    });

    // --- 2. Live Text Counters ---
    function updateCounters() {
        const text = sourceText.value || "";
        const chars = text.length;
        const words = text.trim() ? text.trim().split(/\s+/).length : 0;
        charCount.textContent = `${chars} / 5000`;
        wordCount.textContent = `${words} words`;
    }

    sourceText.addEventListener("input", updateCounters);

    // --- 3. Clear Input & Output ---
    clearInputBtn.addEventListener("click", () => {
        sourceText.value = "";
        targetText.textContent = "";
        targetText.style.display = "none";
        outputPlaceholder.style.display = "flex";
        detectedBadge.style.display = "none";
        providerBadge.style.display = "none";
        resultStats.textContent = "";
        updateCounters();
        sourceText.focus();
    });

    // --- 4. Language Swap ---
    swapLanguagesBtn.addEventListener("click", () => {
        const currentSource = sourceLangSelect.value;
        const currentTarget = targetLangSelect.value;
        const currentResultText = targetText.textContent.trim();

        // Swap target to source
        let newSource = currentTarget;
        let newTarget = currentSource === "auto" ? (lastDetectedCode || "en") : currentSource;

        const supportedCodes = Array.from(targetLangSelect.options).map((o) => o.value);
        if (newTarget === "auto" || !supportedCodes.includes(newTarget)) {
            newTarget = "en";
        }

        sourceLangSelect.value = newSource;
        targetLangSelect.value = newTarget;

        if (currentResultText) {
            sourceText.value = currentResultText;
            targetText.textContent = "";
            targetText.style.display = "none";
            outputPlaceholder.style.display = "flex";
            updateCounters();
            triggerTranslation();
        }
    });

    // --- 5. Sample Cards Click / Keyboard Activation ---
    sampleTriggers.forEach((card) => {
        const useSample = () => {
            const sample = card.getAttribute("data-sample");
            if (sample) {
                sourceText.value = sample;
                updateCounters();
                triggerTranslation();
            }
        };
        card.addEventListener("click", useSample);
        card.addEventListener("keydown", (e) => {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                useSample();
            }
        });
    });

    // --- 6. Keyboard Shortcut (Ctrl/Cmd + Enter) ---
    sourceText.addEventListener("keydown", (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
            e.preventDefault();
            triggerTranslation();
        }
    });

    translateBtn.addEventListener("click", () => {
        triggerTranslation();
    });

    // --- 7. Translation Request Handler ---
    async function triggerTranslation() {
        const text = sourceText.value.trim();
        if (!text) {
            showToast("Please enter text to translate.", "error");
            sourceText.focus();
            return;
        }

        if (isTranslating) return;
        setLoading(true);

        const source = sourceLangSelect.value;
        const target = targetLangSelect.value;

        try {
            const response = await fetch("/api/translate", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    text: text,
                    source: source,
                    target: target
                })
            });

            const data = await response.json();

            if (!response.ok || data.status !== "success") {
                throw new Error(data.message || "Failed to translate text.");
            }

            // Display translated result
            outputPlaceholder.style.display = "none";
            targetText.textContent = data.translated_text;
            targetText.style.display = "block";

            // Update stats & badges
            const resultWords = data.translated_text.trim().split(/\s+/).length;
            resultStats.textContent = `${data.translated_text.length} chars • ${resultWords} words`;

            if (source === "auto" && data.detected_source) {
                detectedBadge.style.display = "inline-block";
                detectedLangName.textContent = data.detected_source;
                lastDetectedCode = data.source_code;
            } else {
                detectedBadge.style.display = "none";
            }

            if (data.provider) {
                providerBadge.textContent = data.provider;
                providerBadge.style.display = "inline-block";
            }

            // Save to history
            saveToHistory({
                sourceText: text,
                translatedText: data.translated_text,
                sourceLang: source === "auto" ? data.detected_source : sourceLangSelect.options[sourceLangSelect.selectedIndex].text,
                targetLang: targetLangSelect.options[targetLangSelect.selectedIndex].text,
                sourceCode: data.source_code,
                targetCode: target,
                timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
            });

        } catch (err) {
            console.error("Translation error:", err);
            showToast(err.message || "An error occurred while translating.", "error");
        } finally {
            setLoading(false);
        }
    }

    function setLoading(loading) {
        isTranslating = loading;
        if (loading) {
            btnSpinner.style.display = "inline-block";
            btnText.textContent = "Translating...";
            translateBtn.disabled = true;
        } else {
            btnSpinner.style.display = "none";
            btnText.textContent = "Translate Text";
            translateBtn.disabled = false;
        }
    }

    // --- 8. Copy to Clipboard ---
    copyResultBtn.addEventListener("click", async () => {
        const textToCopy = targetText.textContent.trim();
        if (!textToCopy) {
            showToast("No translated text to copy yet!", "error");
            return;
        }

        try {
            if (navigator.clipboard && window.isSecureContext) {
                await navigator.clipboard.writeText(textToCopy);
            } else {
                const tempTextArea = document.createElement("textarea");
                tempTextArea.value = textToCopy;
                document.body.appendChild(tempTextArea);
                tempTextArea.select();
                document.execCommand("copy");
                document.body.removeChild(tempTextArea);
            }

            copyResultBtn.classList.add("copied");
            copyBtnText.textContent = "Copied!";
            copyIconDefault.style.display = "none";
            copyIconSuccess.style.display = "inline-block";

            showToast("Copied to clipboard!", "success");

            setTimeout(() => {
                copyResultBtn.classList.remove("copied");
                copyBtnText.textContent = "Copy";
                copyIconDefault.style.display = "inline-block";
                copyIconSuccess.style.display = "none";
            }, 2000);
        } catch (err) {
            console.error("Copy failed:", err);
            showToast("Unable to copy to clipboard.", "error");
        }
    });

    // --- 9. History Management (localStorage) ---
    function getHistory() {
        try {
            return JSON.parse(localStorage.getItem("codealpha_history")) || [];
        } catch {
            return [];
        }
    }

    function saveToHistory(item) {
        let history = getHistory();
        if (history.length > 0 && history[0].sourceText === item.sourceText && history[0].targetCode === item.targetCode) {
            return;
        }
        history.unshift(item);
        if (history.length > 8) {
            history = history.slice(0, 8);
        }
        localStorage.setItem("codealpha_history", JSON.stringify(history));
        renderHistory();
    }

    function renderHistory() {
        const history = getHistory();
        if (history.length === 0) {
            historyList.innerHTML = `<div class="history-empty-item">No recent translations yet. Enter text above to start!</div>`;
            return;
        }

        historyList.innerHTML = "";
        history.forEach((entry, idx) => {
            const item = document.createElement("div");
            item.className = "history-card-item";
            item.setAttribute("role", "button");
            item.setAttribute("tabindex", "0");
            item.innerHTML = `
                <div class="history-item-left">
                    <div class="history-icon-circle">✦</div>
                    <div class="history-item-texts">
                        <span class="history-item-title">${escapeHtml(entry.sourceLang)} → ${escapeHtml(entry.targetLang)}</span>
                        <span class="history-item-sub">${escapeHtml(entry.sourceText)}</span>
                    </div>
                </div>
                <div class="history-item-right">
                    <span class="history-item-arrow">›</span>
                </div>
            `;

            // Click or press Enter/Space to reload the item into the translator
            const loadEntry = () => {
                sourceText.value = entry.sourceText;
                if (entry.sourceCode) sourceLangSelect.value = entry.sourceCode;
                if (entry.targetCode) targetLangSelect.value = entry.targetCode;
                targetText.textContent = entry.translatedText;
                targetText.style.display = "block";
                outputPlaceholder.style.display = "none";
                updateCounters();
                showToast("Loaded from history", "info");
            };
            item.addEventListener("click", loadEntry);
            item.addEventListener("keydown", (e) => {
                if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    loadEntry();
                }
            });

            historyList.appendChild(item);
        });
    }

    clearHistoryBtn.addEventListener("click", () => {
        localStorage.removeItem("codealpha_history");
        renderHistory();
        showToast("Translation history cleared", "info");
    });

    // Helper: Escape HTML
    function escapeHtml(str) {
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // --- 10. Toast Notifications ---
    function showToast(message, type = "info") {
        const toast = document.createElement("div");
        toast.className = `toast ${type === "error" ? "toast-error" : type === "success" ? "toast-success" : ""}`;
        toast.textContent = message;

        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = "0";
            toast.style.transition = "opacity 0.3s ease";
            setTimeout(() => {
                if (toast.parentElement) toast.parentElement.removeChild(toast);
            }, 300);
        }, 2600);
    }

    // Initial render
    renderHistory();
    updateCounters();
});
