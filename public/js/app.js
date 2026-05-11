(function () {
    var userInput = document.getElementById("user-input");
    var languageSelect = document.getElementById("language-select");
    var frameworkSelect = document.getElementById("framework-select");
    var databaseSelect = document.getElementById("database-select");
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
    var themeIconSun = document.getElementById("theme-icon-sun");
    var themeIconMoon = document.getElementById("theme-icon-moon");

    var selectedType = null;
    var lastRequest = null;

    var TYPE_LUCIDE = {
        system: "monitor",
        start: "rocket",
        followup: "repeat",
        debug: "bug",
    };

    var TYPE_LABELS = {
        system: "System Prompt",
        start: "Start Prompt",
        followup: "Follow-Up",
        debug: "Debugging",
    };

    lucide.createIcons();

    function setThemeIcons(isDark) {
        if (isDark) {
            themeIconSun.classList.add("hidden");
            themeIconMoon.classList.remove("hidden");
        } else {
            themeIconSun.classList.remove("hidden");
            themeIconMoon.classList.add("hidden");
        }
    }

    function initTheme() {
        var stored = localStorage.getItem("zprompt-theme");
        if (stored === "light") {
            document.documentElement.classList.remove("dark");
            setThemeIcons(false);
        } else {
            document.documentElement.classList.add("dark");
            setThemeIcons(true);
        }
    }

    themeToggle.addEventListener("click", function () {
        var isDark = document.documentElement.classList.toggle("dark");
        localStorage.setItem("zprompt-theme", isDark ? "dark" : "light");
        setThemeIcons(isDark);
    });

    initTheme();

    function selectType(type) {
        document.querySelectorAll(".prompt-type-card").forEach(function (c) {
            c.classList.remove(
                "border-primary",
                "bg-primary/10",
                "ring-2",
                "ring-ring"
            );
        });
        var card = document.querySelector('[data-type="' + type + '"]');
        if (card) {
            card.classList.add(
                "border-primary",
                "bg-primary/10",
                "ring-2",
                "ring-ring"
            );
        }
        selectedType = type;
        validateForm();
    }

    document.querySelectorAll(".prompt-type-card").forEach(function (card) {
        card.addEventListener("click", function () {
            selectType(card.dataset.type);
        });
    });

    selectType("start");

    userInput.addEventListener("input", validateForm);

    userInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            if (!generateBtn.disabled) {
                handleGenerate();
            }
        }
    });

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
            database: databaseSelect.value || null,
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
            btnText.textContent = "GENERAR PROMPT";
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

    function formatLocalDate(date) {
        var offset = cachedOffset !== null ? cachedOffset : (-new Date().getTimezoneOffset());
        var localDate = new Date(date.getTime() + (date.getTimezoneOffset() * 60000) + (offset * 60000));
        var d = localDate.getDate();
        var mo = localDate.getMonth() + 1;
        var y = localDate.getFullYear();
        var h = localDate.getHours();
        var m = localDate.getMinutes();
        var s = localDate.getSeconds();
        return (d < 10 ? "0" : "") + d + "/" + (mo < 10 ? "0" : "") + mo + "/" + y + ", " + (h < 10 ? "0" : "") + h + ":" + (m < 10 ? "0" : "") + m + ":" + (s < 10 ? "0" : "") + s;
    }

    function showResult(data) {
        var iconName = TYPE_LUCIDE[data.prompt_type] || "file-text";
        resultIcon.innerHTML = '<i data-lucide="' + iconName + '" class="h-4 w-4"></i>';
        resultTitle.textContent = data.label || TYPE_LABELS[data.prompt_type] || "Prompt";
        resultContent.textContent = data.prompt;
        resultTimestamp.textContent = "Generado: " + formatLocalDate(new Date());
        resultSection.classList.remove("hidden");
        lucide.createIcons();
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
            copyBtn.innerHTML = '<i data-lucide="check" class="h-3.5 w-3.5"></i> Copiado!';
            lucide.createIcons();
            setTimeout(function () {
                copyBtn.innerHTML = '<i data-lucide="copy" class="h-3.5 w-3.5"></i> Copiar';
                lucide.createIcons();
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
            copyBtn.innerHTML = '<i data-lucide="check" class="h-3.5 w-3.5"></i> Copiado!';
            lucide.createIcons();
            setTimeout(function () {
                copyBtn.innerHTML = '<i data-lucide="copy" class="h-3.5 w-3.5"></i> Copiar';
                lucide.createIcons();
            }, 2000);
        }
    });

    function offsetToTzName(offset) {
        var offsetH = Math.floor(Math.abs(offset) / 60);
        var offsetM = Math.abs(offset) % 60;
        var sign = offset >= 0 ? "+" : "-";
        return "UTC" + sign + (offsetH < 10 ? "0" : "") + offsetH + ":" + (offsetM < 10 ? "0" : "") + offsetM;
    }

    var cachedOffset = null;

    (function loadCachedTz() {
        var cached = localStorage.getItem("zprompt-tz-offset");
        if (cached !== null) {
            cachedOffset = parseInt(cached, 10);
        }
    })();

    async function detectOffsetAsync() {
        var browserOffset = -new Date().getTimezoneOffset();
        if (browserOffset !== 0) {
            cachedOffset = browserOffset;
            return;
        }
        try {
            var tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
            if (tz && tz !== "UTC") {
                cachedOffset = browserOffset;
                return;
            }
        } catch (e) {}

        if (cachedOffset !== null && cachedOffset !== 0) {
            return;
        }

        async function tryIpwhois() {
            try {
                var r = await fetch("https://ipwho.is/");
                var d = await r.json();
                if (d && d.timezone && d.timezone.offset != null) {
                    var m = Math.round(d.timezone.offset / 60);
                    if (m !== 0) return m;
                }
            } catch (e) {}
            return null;
        }

        async function tryIpapi() {
            try {
                var r = await fetch("https://ipapi.co/json/");
                var d = await r.json();
                if (d && d.utc_offset) {
                    var s = d.utc_offset;
                    var sign = s.charAt(0) === "+" ? 1 : -1;
                    var h = parseInt(s.substring(1, 3), 10);
                    var mm = parseInt(s.substring(3, 5), 10);
                    var total = sign * (h * 60 + mm);
                    if (total !== 0) return total;
                }
            } catch (e) {}
            return null;
        }

        async function tryWorldTimeApi() {
            try {
                var r = await fetch("https://worldtimeapi.org/api/ip");
                var d = await r.json();
                if (d && d.utc_offset) {
                    var s = d.utc_offset;
                    var sign = s.charAt(0) === "+" ? 1 : -1;
                    var parts = s.substring(1).split(":");
                    var h = parseInt(parts[0], 10);
                    var mm = parseInt(parts[1], 10);
                    var total = sign * (h * 60 + mm);
                    if (total !== 0) return total;
                }
            } catch (e) {}
            return null;
        }

        async function tryServerApi() {
            try {
                var r = await fetch("/api/timezone");
                var d = await r.json();
                if (d && d.offset && d.offset !== 0) return d.offset;
            } catch (e) {}
            return null;
        }

        var offset = await tryIpwhois() || await tryIpapi() || await tryWorldTimeApi() || await tryServerApi();

        if (offset) {
            cachedOffset = offset;
            localStorage.setItem("zprompt-tz-offset", offset);
            updatePeakInfo();
        } else {
            cachedOffset = 0;
        }
    }

    detectOffsetAsync();

    function updatePeakInfo() {
        var now = new Date();
        var offset = cachedOffset !== null ? cachedOffset : (-new Date().getTimezoneOffset());

        var offsetStr = offsetToTzName(offset);

        var localDate = new Date(now.getTime() + (now.getTimezoneOffset() * 60000) + (offset * 60000));
        var localH = localDate.getHours();
        var localM = localDate.getMinutes();
        var timeStr = (localH < 10 ? "0" : "") + localH + ":" + (localM < 10 ? "0" : "") + localM;

        var utcH = now.getUTCHours();
        var isPeak = utcH >= 6 && utcH < 10;
        var status = isPeak ? "PEAK" : "OFF-PEAK";
        var statusColor = isPeak ? "text-destructive" : "text-primary";
        var msg = isPeak ? "Horas pico - uso limitado" : "Buen momento para usar GLM";

        var peakStartUTC = 6;
        var peakEndUTC = 10;
        var localOffsetH = offset / 60;
        var peakStartLocal = (peakStartUTC + localOffsetH + 24) % 24;
        var peakEndLocal = (peakEndUTC + localOffsetH + 24) % 24;
        var peakLocalStartStr = (peakStartLocal < 10 ? "0" : "") + Math.floor(peakStartLocal) + ":00";
        var peakLocalEndStr = (peakEndLocal < 10 ? "0" : "") + Math.floor(peakEndLocal) + ":00";

        var el = document.getElementById("peak-info");
        if (!el) return;
        el.innerHTML =
            '<p class="' + statusColor + ' font-semibold">' + status + ' &middot; ' + msg + '</p>' +
            '<p class="mt-1">Tu hora: ' + timeStr + ' (' + offsetStr + ') &middot; Peak local: ' + peakLocalStartStr + ' - ' + peakLocalEndStr + '</p>' +
            '<p class="mt-1">GLM-5.1: 3x peak / 2x off-peak &middot; <span class="text-primary">1x off-peak hasta fin de junio</span></p>';
    }
    updatePeakInfo();
    setInterval(updatePeakInfo, 60000);
})();
