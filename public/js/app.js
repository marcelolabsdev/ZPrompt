(function () {
    var userInput = document.getElementById("user-input");
    var languageSelect = document.getElementById("language-select");
    var frameworkSelect = document.getElementById("framework-select");
    var generateBtn = document.getElementById("generate-btn");
    var btnText = document.getElementById("btn-text");
    var btnSpinner = document.getElementById("btn-spinner");
    var errorSection = document.getElementById("error-section");
    var errorMessage = document.getElementById("error-message");
    var resultSection = document.getElementById("result-section");
    var resultIcon = document.getElementById("result-icon");
    var resultTitle = document.getElementById("result-title");
    var resultContent = document.getElementById("result-content");
    var resultTimestamp = document.getElementById("result-timestamp");
    var copyBtn = document.getElementById("copy-btn");
    var regenerateBtn = document.getElementById("regenerate-btn");
    var themeToggle = document.getElementById("theme-toggle");
    var themeIcon = document.getElementById("theme-icon");

    var selectedType = null;
    var lastRequest = null;

    var TYPE_ICONS = {
        system: "🖥️",
        start: "🚀",
        followup: "🔄",
        debug: "🐛",
    };

    var TYPE_LABELS = {
        system: "System Prompt",
        start: "Start Prompt",
        followup: "Follow-Up",
        debug: "Debugging",
    };

    function initTheme() {
        var stored = localStorage.getItem("zprompt-theme");
        if (stored === "light") {
            document.documentElement.classList.remove("dark");
            themeIcon.textContent = "🌙";
        } else {
            document.documentElement.classList.add("dark");
            themeIcon.textContent = "☀️";
        }
    }

    themeToggle.addEventListener("click", function () {
        var isDark = document.documentElement.classList.toggle("dark");
        localStorage.setItem("zprompt-theme", isDark ? "dark" : "light");
        themeIcon.textContent = isDark ? "☀️" : "🌙";
    });

    initTheme();

    document.querySelectorAll(".prompt-type-card").forEach(function (card) {
        card.addEventListener("click", function () {
            document.querySelectorAll(".prompt-type-card").forEach(function (c) {
                c.classList.remove(
                    "border-primary",
                    "bg-primary/10",
                    "ring-2",
                    "ring-ring"
                );
            });
            card.classList.add(
                "border-primary",
                "bg-primary/10",
                "ring-2",
                "ring-ring"
            );
            selectedType = card.dataset.type;
            validateForm();
        });
    });

    userInput.addEventListener("input", validateForm);

    function validateForm() {
        var hasText = userInput.value.trim().length >= 5;
        var hasType = selectedType !== null;
        generateBtn.disabled = !(hasText && hasType);
    }

    generateBtn.addEventListener("click", handleGenerate);
    regenerateBtn.addEventListener("click", handleGenerate);

    async function handleGenerate() {
        var text = userInput.value.trim();
        if (text.length < 5 || !selectedType) return;

        lastRequest = {
            text: text,
            prompt_type: selectedType,
            language: languageSelect.value || null,
            framework: frameworkSelect.value || null,
        };

        setLoading(true);
        hideError();
        hideResult();

        try {
            var response = await fetch("/api/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(lastRequest),
            });

            var data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Error generando el prompt");
            }

            showResult(data);
        } catch (err) {
            showError(err.message);
        } finally {
            setLoading(false);
        }
    }

    function setLoading(loading) {
        generateBtn.disabled = loading;
        if (loading) {
            btnText.textContent = "Generando...";
            btnSpinner.classList.remove("hidden");
        } else {
            btnText.textContent = "⚡ Generar Prompt";
            btnSpinner.classList.add("hidden");
        }
    }

    function showError(msg) {
        errorMessage.textContent = msg;
        errorSection.classList.remove("hidden");
    }

    function hideError() {
        errorSection.classList.add("hidden");
    }

    function showResult(data) {
        resultIcon.textContent = TYPE_ICONS[data.prompt_type] || "📄";
        resultTitle.textContent = data.label || TYPE_LABELS[data.prompt_type] || "Prompt";
        resultContent.textContent = data.prompt;
        resultTimestamp.textContent = "Generado: " + new Date().toLocaleString("es-ES");
        resultSection.classList.remove("hidden");
        resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    function hideResult() {
        resultSection.classList.add("hidden");
    }

    copyBtn.addEventListener("click", async function () {
        var text = resultContent.textContent;
        if (!text) return;
        try {
            await navigator.clipboard.writeText(text);
            copyBtn.textContent = "✅ Copiado!";
            setTimeout(function () {
                copyBtn.textContent = "📋 Copiar";
            }, 2000);
        } catch {
            var textarea = document.createElement("textarea");
            textarea.value = text;
            textarea.style.position = "fixed";
            textarea.style.opacity = "0";
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand("copy");
            document.body.removeChild(textarea);
            copyBtn.textContent = "✅ Copiado!";
            setTimeout(function () {
                copyBtn.textContent = "📋 Copiar";
            }, 2000);
        }
    });
})();
