const orb = document.querySelector(".orb");
const entry = document.querySelector(".entry");
const discovery = document.querySelector(".discovery");

const title = document.getElementById("title");
const reveal = document.getElementById("reveal");
const meaning = document.getElementById("meaning");

const save = document.getElementById("save");
const share = document.getElementById("share");

let data = null;
let opened = false;

const fallback = {
    id: "fallback",
    category: "COSMOS",
    title_en: "THE SUN IS NOT YELLOW",
    title_zh: "太阳其实不是黄色的",
    reveal_en:
        "From space, the Sun appears white. Earth's atmosphere changes the color we experience from the ground.",
    reveal_zh:
        "从太空看，太阳其实呈现白色。地球大气层改变了我们从地面看到的颜色。",
    meaning_en:
        "Reality can change with the distance between what exists and what we perceive.",
    meaning_zh:
        "我们看到的现实，往往受到观察距离和方式的影响。",
    visual: {
        theme: "cosmos",
        color: "#7B8CFF"
    }
};

const VISUAL_SYSTEMS = {
    COSMOS:  { theme: "cosmos", color: "#7B8CFF" },
    NATURE:  { theme: "nature", color: "#7FD6A4" },
    SCIENCE: { theme: "science", color: "#6FD8FF" },
    HUMAN:   { theme: "human", color: "#E0A978" },
    ART:     { theme: "art", color: "#C49BFF" },
    CULTURE: { theme: "culture", color: "#D7B98A" },
    TIME:    { theme: "time", color: "#AEB8C8" },
    LIFE:    { theme: "life", color: "#91E6C1" }
};

async function loadContent() {
    try {
        const response = await fetch(
            "./content/today.json?v=" + Date.now(),
            { cache: "no-store" }
        );

        if (!response.ok) {
            throw new Error(
                "Content loading failed: " +
                response.status
            );
        }

        const json = await response.json();
        data = normalizeContent(json);
    } catch (error) {
        console.warn(
            "ONE THING content fallback:",
            error
        );

        data = fallback;
    }

    renderContent();
    applyVisual();
}

function normalizeContent(source) {
    return {
        id:
            source.id ||
            "one-thing",

        category:
            source.category ||
            "COSMOS",

        title_en:
            source.title_en ||
            source.title?.en ||
            "",

        title_zh:
            source.title_zh ||
            source.title?.zh ||
            "",

        reveal_en:
            source.reveal_en ||
            source.reveal?.en ||
            "",

        reveal_zh:
            source.reveal_zh ||
            source.reveal?.zh ||
            "",

        meaning_en:
            source.meaning_en ||
            source.meaning?.en ||
            "",

        meaning_zh:
            source.meaning_zh ||
            source.meaning?.zh ||
            "",

        visual:
            source.visual ||
            {
                theme: "cosmos",
                color: "#ffffff"
            }
    };
}

function renderContent() {
    title.innerHTML = `
        <div class="english">
            ${escapeHTML(data.title_en)}
        </div>
        <div class="chinese">
            ${escapeHTML(data.title_zh)}
        </div>
    `;

    reveal.innerHTML = `
        <div class="english">
            ${escapeHTML(data.reveal_en)}
        </div>
        <div class="chinese">
            ${escapeHTML(data.reveal_zh)}
        </div>
    `;

    meaning.innerHTML = `
        <div class="english">
            ${escapeHTML(data.meaning_en)}
        </div>
        <div class="chinese">
            ${escapeHTML(data.meaning_zh)}
        </div>
    `;
}

function escapeHTML(value) {
    return String(value || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function getVisualSystem() {
    const category =
        String(data?.category || "COSMOS")
            .toUpperCase();

    const preset =
        VISUAL_SYSTEMS[category] ||
        VISUAL_SYSTEMS.COSMOS;

    const suppliedColor =
        data?.visual?.color;

    const suppliedTheme =
        String(data?.visual?.theme || "")
            .toLowerCase();

    const color =
        typeof suppliedColor === "string" &&
        /^#[0-9a-fA-F]{6}$/.test(
            suppliedColor.trim()
        )
            ? suppliedColor.trim()
            : preset.color;

    const allowedThemes =
        new Set(
            Object.values(VISUAL_SYSTEMS)
                .map(item => item.theme)
        );

    const theme =
        allowedThemes.has(suppliedTheme)
            ? suppliedTheme
            : preset.theme;

    return {
        theme,
        color
    };
}

function applyVisual() {
    const visual =
        getVisualSystem();

    document.documentElement.style.setProperty(
        "--theme",
        visual.color
    );

    document.body.dataset.theme =
        visual.theme;
}

function enterDiscovery() {
    if (opened || !data) {
        return;
    }

    opened = true;

    document.body.classList.add(
        "opening"
    );

    orb.classList.add(
        "portal"
    );

    entry.classList.add(
        "vanish"
    );

    setTimeout(() => {
        orb.style.display = "none";
        entry.style.display = "none";

        discovery.classList.remove(
            "hidden"
        );

        requestAnimationFrame(() => {
            discovery.classList.add(
                "revealed"
            );
        });

        document.body.classList.remove(
            "opening"
        );
    }, 900);
}

orb.addEventListener(
    "click",
    enterDiscovery
);

entry.addEventListener(
    "click",
    enterDiscovery
);

save.addEventListener(
    "click",
    () => {
        localStorage.setItem(
            "ONE_THING_SAVE",
            JSON.stringify(data)
        );

        save.innerText = "SAVED";
    }
);

share.addEventListener(
    "click",
    async () => {
        const text = `
${data.title_en}
${data.title_zh}

${data.reveal_en}
${data.reveal_zh}

${data.meaning_en}
${data.meaning_zh}

— ONE THING
`;

        try {
            if (navigator.share) {
                await navigator.share({
                    title: "ONE THING",
                    text: text
                });
            } else {
                await navigator.clipboard.writeText(
                    text
                );

                share.innerText = "COPIED";
            }
        } catch (error) {
            console.log(
                "Share cancelled"
            );
        }
    }
);

document.addEventListener(
    "keydown",
    event => {
        if (
            event.key === "Enter"
        ) {
            enterDiscovery();
        }
    }
);

loadContent();
